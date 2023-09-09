#!/usr/bin/env python3
# coding: utf-8
"""
https://www.reddit.com/r/olkb/comments/x00jyo/cannot_send_or_receive_data_with_raw_hid_feature/
"""
import time
import json
import fire
import ctypes
from send_kmk import send_kmk


def get_config(path):
    with open(path, "r", encoding="utf-8") as file:
        config = json.load(file)
        for c in config["config_array"]:
            for i in ["vid", "pid", "usage_page", "usage_id"]:
                if i in c:
                    n = c[i]
                    if type(n) == str:
                        c[i] = int(n, 16)
        return config


def pad_message(payload: bytes) -> bytes:
    if len(payload) > EP_SIZE:
        raise (f"payload is too large: maximum payload is {str(EP_SIZE)}")
    return payload + b"\xff" * (EP_SIZE - len(payload))


def to_bytes(data: str) -> bytes:
    return data.encode()


def find_device(vid, pid, usage_page, usage_id):
    for device in hid.enumerate():
        if (
            device["vendor_id"] == vid
            and device["product_id"] == pid
            and device["usage_page"] == usage_page
            and device["usage"] == usage_id
        ):
            keyboard = hid.Device(path=device["path"])
            return keyboard


def send_device(sendList, keyboard, enable_received=None):
    sendList = [1 if sendList[0] == "switch_layer" else 0, sendList[1]]
    message = pad_message(bytes(sendList))
    message = (
        b"\x00" + message[0 : EP_SIZE - 1]
    )  # 因为第0个比特会被 raw_hid_receive 吞掉,所以用第1个位置的比特
    print("sending_qmk:", message, len(message))
    keyboard.write(message)
    if enable_received:
        print(f"reading... wait {sleepTime} second")
        time.sleep(sleepTime)
        received = keyboard.read(EP_SIZE)
        print("received:", received, len(received))
    keyboard.close()


def show_device_list():
    for device in hid.enumerate():
        print(
            f"product_string: {device['product_string']}\n"
            f"manufacturer_string: {device['manufacturer_string']}\n"
            f"vendor_id: {device['vendor_id']}\n"
            f"product_id: {device['product_id']}\n"
            f"usage_page: {device['usage_page']}\n"
            f"usage: {device['usage']}\n"
        )


def config(configPath, sendList=None, device_list=None, enable_received=None):
    config = get_config(configPath)
    if sendList:
        config["sendList"] = sendList
    main(
        config["config_array"],
        config["sendList"],
        config["dllPath"],
        config["EP_SIZE"],
        config["sleepTime"],
        device_list,
        enable_received,
    )


def main(
    config_array,
    sendList,
    dllPath,
    _EP_SIZE,
    _sleepTime,
    device_list,
    enable_received,
):
    global hid, EP_SIZE, sleepTime
    ctypes.CDLL(dllPath)
    import hid as _hid

    hid = _hid
    EP_SIZE = _EP_SIZE
    sleepTime = _sleepTime

    if device_list:
        show_device_list()
        return

    for c in config_array:
        if c["type"] == "qmk":
            keyboard = find_device(c["vid"], c["pid"], c["usage_page"], c["usage_id"])
            if keyboard:
                print(
                    "---qmk---",
                )
                print(
                    f"Product: {keyboard.product} vid: {c['vid']} pid: {c['pid']} usage_page: {c['usage_page']} usage_id: {c['usage_id']}",
                )
                send_device(sendList, keyboard)
            else:
                print("---qmk---")
                print(
                    "qmk keyboard was not found.",
                    f"vid: {c['vid']} pid: {c['pid']} usage_page: {c['usage_page']} usage_id: {c['usage_id']}",
                )
        if c["type"] == "kmk":
            print("---kmk---")
            send_kmk(c, sendList)


def show():
    config("config.json", device_list=True)


if __name__ == "__main__":
    fire.Fire({"args": args, "config": config, "show": show})
