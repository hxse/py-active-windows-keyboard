# py-active-windows-keyboard
# config.json
  * modify `example.json` to create `config.json`

# QMK send hid
  * qmk需要用hidapi,kmk不需要用这个
  * download, https://github.com/libusb/hidapi/releases
  * 方式一,通过配置文件
    * `pdm run python .\send_hid.py config ".\config.json"`
    * create config.json
    * sendList字段,是个数组,0-255范围,在示例中的第一个数字表达模式,第二个数字表达切换图层
    * dllPath 是hidapi的本地dll路径
    * EP_SIZE ATMEGA32U4通常需要32字节大小
    * sleepTime,检测桌系统窗口状态的轮询间隔
    * escapList,对于规则不匹配的漏网之鱼,要通过hid发送的数组
  * 方式二,通过参数
  * `pdm run python .\send_hid.py args [1,5]  0x45d4 0x0911 0xFF60 0x61 "D:\App\app\hidapi\hidapi-win\x64\hidapi.dll" 32 0.2`
  * 如何找到设备信息
    * --device_list 1 这个参数可以打印找到devices的信息
    * vid,pid,可以在qmk方案中的info.json文件里找到
    * usage_page,usage_id,可以在qmk方案中的config.h文件里找到RAW_USAGE_PAGE,RAW_USAGE_ID,qmk中的方案默认是0xFF60,0x61
# KMK send serial
  * `python -m serial.tools.list_ports` on widnows run this code to find ports and write port in config.json
  * run with kmk code https://github.com/hxse/piantor_kmk_firmware/blob/main/serialace2.py
# active_window.py
  * `pdm run python .\active_window.py --path config.json`
  * title,process,支持正则表达式
  * \斜杠应该用双斜杠转义
  * skip为true时,忽略规则匹配,自动进入漏网规则,为false时正常进入规则匹配
# autohotkey script
  * ahk_file_name,ahk脚本的名字,可以不填,默认为,keyboard_mapping.ahk
  * hidden_ahk_tray,是否隐藏ahk脚本的托盘图标,可以不填,默认为true,隐藏图标
  * hidden_ahk_print,是否隐藏ahk日志打印,可以不填,默认为flash,不隐藏
  * hidden_ahk_print_script,是否打印详细脚本内容,可以不填,默认为true,打印,如果hidden_ahk_print为false,则不打印
  * skip_mapping是否跳过ahk的键盘映射,true则跳过脚本
  * ahk_code,就是ahk命令,数组中每个元素一行
