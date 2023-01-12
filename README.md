# py-active-windows-keyboard
# send_hid.py
  * download, https://github.com/libusb/hidapi/releases
  * 方式一,通过配置文件
    * `pdm run python .\send_hid.py config ".\config.json"`
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
    * dllPath 是hidapi的本地dll路径
    * EP_SIZE ATMEGA32U4通常需要32字节大小
  * 方式二,通过参数
  * `pdm run python .\send_hid.py args [1,5]  0x45d4 0x0911 0xFF60 0x61 "D:\App\app\hidapi\hidapi-win\x64\hidapi.dll" 32 0.2`
  * 如何找到设备信息
    * --device_list 1 这个参数可以打印找到devices的信息
    * vid,pid,可以在qmk方案中的info.json文件里找到
    * usage_page,usage_id,可以在qmk方案中的config.h文件里找到RAW_USAGE_PAGE,RAW_USAGE_ID,qmk中的方案默认是0xFF60,0x61
# active_window.py
  * `pdm run python .\active_window.py --path config.json`
  * ```
    "condition": [
      {
      "title": ".*Visual Studio Code",
      "process": "C:\\Users\\hxse\\scoop\\apps\\vscode\\.*\\Code.exe",
      "send": [1, 0],
      "skip": false
      }
    ]
    ```
  * title,process,支持正则表达式
  * \斜杠应该用双斜杠转义
  * skip为true时,忽略规则匹配,自动进入漏网规则,为false时正常进入规则匹配
