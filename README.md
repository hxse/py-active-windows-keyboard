# py-active-windows-keyboard
  * download https://github.com/libusb/hidapi/releases
  * add path: `ctypes.CDLL(r"C:\Users\hxse\Downloads\hidapi.dll")`
  * create config.json
  *
    ```
    {
    "EP_SIZE": 32,
    "vid": "0x45d4",
    "pid": "0x0911",
    "usage_page": "0xFF60",
    "usage_id": "0x61",
    "sleepTime": 0.2,
    "sendList": [1, 5]
    }
    ```
