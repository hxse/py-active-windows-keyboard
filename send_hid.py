#!/usr/bin/env python3
# coding: utf-8
"""
https://www.reddit.com/r/olkb/comments/x00jyo/cannot_send_or_receive_data_with_raw_hid_feature/
"""
import time
import json
import fire
import ctypes


def get_config(path):
    with open(path, "r", encoding="utf-8") as file:
        config = json.load(file)
        for i in ["vid", "pid", "usage_page", "usage_id"]:
            c = config[i]
            if type(c) == str:
                config[i] = int(c, 16)
        return {
            "EP_SIZE": config[
                "EP_SIZE"
            ],  # ATMEGA32U4通常需要32字节大小,超出会自动截断 #更新,好像不用这个也行,不确定
            "vid": config["vid"],
            "pid": config["pid"],
            "usage_page": config["usage_page"],
            "usage_id": config["usage_id"],
            "sendList": config["sendList"],
            "sleepTime": config["sleepTime"],
            "dllPath": config["dllPath"],
        }


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
    message = pad_message(bytes(sendList))
    message = (
        b"\x00" + message[0 : EP_SIZE - 1]
    )  # 因为第0个比特会被 raw_hid_receive 吞掉,所以用第1个位置的比特
    print("sending:", message, len(message))
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


def args(
    sendList,
    vid,
    pid,
    usage_page,
    usage_id,
    dllPath,
    EP_SIZE=32,
    sleepTime=0.2,
    device_list=None,
    enable_received=None,
):
    main(
        sendList,
        vid,
        pid,
        usage_page,
        usage_id,
        dllPath,
        EP_SIZE,
        sleepTime,
        device_list,
        enable_received,
    )


def config(configPath, sendList=None, device_list=None, enable_received=None):
    config = get_config(configPath)
    if sendList:
        config["sendList"] = sendList
    main(
        config["sendList"],
        config["vid"],
        config["pid"],
        config["usage_page"],
        config["usage_id"],
        config["dllPath"],
        config["EP_SIZE"],
        config["sleepTime"],
        device_list,
        enable_received,
    )


def main(
    sendList,
    vid,
    pid,
    usage_page,
    usage_id,
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

    keyboard = find_device(vid, pid, usage_page, usage_id)
    if keyboard:
        print("Product:", keyboard.product)
        print("Manufacturer:", keyboard.manufacturer)
        send_device(sendList, keyboard)
    else:
        print("Keyboard was not found.")


if __name__ == "__main__":
    fire.Fire(
        {
            "args": args,
            "config": config,
        }
    )
