#!/usr/bin/env python3
# coding: utf-8
import serial.tools.list_ports
import time


def show_device():
    # python -m serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    for k, p in enumerate(ports):
        print(f"device {k}", p.description, p.hwid)


def send_kmk(kmk_config, data, enable_received=False, sleepTime=0.3):
    with serial.Serial() as ser:
        # ser.baudrate = 19200
        ser.port = kmk_config["port"]  # on windows example: COM8
        ser.timeout = kmk_config["timeout"]
        try:
            ser.open()
        except serial.serialutil.SerialException as e:
            print(f'kmk Keyboard was not found. port: {kmk_config["port"]}')
            return

        send = b"keyboard.active_layers\n"
        send = b"keyboard.tap_key(KC.Y)\n"
        send = b"keyboard.tap_key(KC.TO(0))\n"
        # send = b"keyboard.tap_key(KC.TO(1))\n"
        send = bytearray(
            f"{ ' '.join([str(i) for i in data])}\n", "utf-8"
        )  # 第一个是模式名字,后面参数,用空格,末尾带\n换行符
        print(f'kmk_name: {kmk_config["name"]} kmk_port: {kmk_config["port"]}')
        print(f"send_kmk: {send}")
        ser.write(send)
        if enable_received:
            print(f"reading... wait {sleepTime} second")
            time.sleep(sleepTime)
            result = ser.readline()
            print(f"result_kmk: {result}")


if __name__ == "__main__":
    show_device()
    # send_kmk()
