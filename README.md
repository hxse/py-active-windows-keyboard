# py-active-windows-keyboard
  * download https://github.com/libusb/hidapi/releases
  * 方式一,通过配置文件
    * `pdm run python .\main.py config ".\config.json"`
    * create config.json
    *
      ```
      {
        "sendList": [1, 5],
        "vid": "0x45d4",
        "pid": "0x0911",
        "usage_page": "0xFF60",
        "usage_id": "0x61",
        "dllPath": "D:\\App\\app\\hidapi\\hidapi-win\\x64\\hidapi.dll",
        "EP_SIZE": 32,
        "sleepTime": 0.2
      }
      ```
    * sendList字段,是个数组,0-255范围,在示例中的第一个数字表达模式,第二个数字表达切换图层
  * 方式二,通过参数
  * `pdm run python .\main.py args [1,5]  0x45d4 0x0911 0xFF60 0x61 "D:\App\app\hidapi\hidapi-win\x64\hidapi.dll" 32 0.2`
