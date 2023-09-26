import json
import re
import time
import win32gui, win32process, psutil
from send_hid import config as send_hid_as_config
import fire
import subprocess
import atexit
import console_print
import pathlib

from console_print import (
    console,
    print_info,
    print_send,
    print_error,
    print_skip,
    print_ahk,
)


def get_config_rules(path):
    global hidden_ahk_tray, hidden_ahk_print, hidden_ahk_print_script
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        rules = data.get("rules")
        skip_escapList = data.get("skip_escapList", False)
        escapList = data.get("escapList", [])
        skip_escapList_ahk = data.get("skip_escapList_ahk", False)
        escapList_ahk = data.get("escapList_ahk", [])
        ahk_file_name = data.get("ahk_file_name", "keyboard_mapping.ahk")
        hidden_ahk_tray = data.get("hidden_ahk_tray", True)
        hidden_ahk_print = data.get("hidden_ahk_print", False)
        hidden_ahk_print_script = data.get("hidden_ahk_print_script", True)
    return [
        rules,
        skip_escapList,  # 目前不用这个,空着就行
        escapList,
        skip_escapList_ahk,
        escapList_ahk,
        ahk_file_name,
    ]


def run_ahk_script(ahk_file_name, ahk_code_list, skip_ahk):
    global ahkCodeFlag, hidden_ahk_tray, hidden_ahk_print, hidden_ahk_print_script
    print_ahk("info", ahk_code_list)
    if skip_ahk or ahk_code_list == []:
        ahk_code_list = ["Pause"]
        if ahkCodeFlag == -1:
            print_ahk("skip")
            return
    if hidden_ahk_tray:
        if ahk_code_list[0] != "#NoTrayIcon":
            ahk_code_list.insert(0, "#NoTrayIcon")
    ahk_code_text = "\n".join(ahk_code_list)
    if ahk_code_text == ahkCodeFlag:
        print_ahk("repeat", ahk_code_list, ahk_code_text)
    else:
        with open(ahk_file_name, "w", encoding="utf8") as f:
            f.write(ahk_code_text)
        print_ahk("script", ahk_code_list, ahk_code_text)

        subprocess.Popen(["autohotkey", "/restart", ahk_file_name])
    ahkCodeFlag = ahk_code_text


last_st_mtime = 0


def check_modify_load_config(path):
    global last_st_mtime
    file = pathlib.Path(path)
    assert file.exists(), f"No such file: {file}"  # check that the file exists
    st_mtime = file.stat().st_mtime
    if st_mtime == last_st_mtime:
        return
    last_st_mtime = st_mtime

    start_time = time.time_ns() // 1000000  # flooring last digit (1ms digit)
    [
        rules,
        skip_escapList,  # 目前不用这个,空着就行
        escapList,
        skip_escapList_ahk,
        escapList_ahk,
        ahk_file_name,
    ] = get_config_rules(path)
    end_time = time.time_ns() // 1000000  # flooring last digit (1ms digit)
    print(f"json config load: {end_time-start_time} ms")
    return [
        rules,
        skip_escapList,  # 目前不用这个,空着就行
        escapList,
        skip_escapList_ahk,
        escapList_ahk,
        ahk_file_name,
    ]


def main(path="config.json", sleepTime=0.3):
    global ahkCodeFlag, hidden_ahk_tray, hidden_ahk_print, hidden_ahk_print_script

    [
        rules,
        skip_escapList,  # 目前不用这个,空着就行
        escapList,
        skip_escapList_ahk,
        escapList_ahk,
        ahk_file_name,
    ] = check_modify_load_config(path)

    console_print.hidden_ahk_print = hidden_ahk_print
    console_print.hidden_ahk_print_script = hidden_ahk_print_script

    appFlag = -1
    layerFlag = -1
    ahkCodeFlag = -1

    def exit_handler(ahk_file_name, ahk_code_list, skip_ahk):
        if ahkCodeFlag == -1:
            print_ahk("skip")
            return
        run_ahk_script(ahk_file_name, ahk_code_list, skip_ahk)

    atexit.register(exit_handler, ahk_file_name, ["exitApp"], False)

    with console.status(
        "[bold green] Wait Windows...", spinner="bouncingBall"
    ) as status:
        while 1:
            time.sleep(sleepTime)

            res = check_modify_load_config(path)
            if res != None:
                appFlag = -1
                layerFlag = -1
                [
                    rules,
                    skip_escapList,
                    escapList,
                    skip_escapList_ahk,
                    escapList_ahk,
                    ahk_file_name,
                ] = res

            window = win32gui.GetForegroundWindow()
            tid, pid = win32process.GetWindowThreadProcessId(window)
            winTitle = win32gui.GetWindowText(window)
            try:
                process = psutil.Process(pid)
                winProcessExe = process.exe()
                winProcessName = process.name()
            except Exception as e:
                print_error("pidError", winTitle, tid, pid, e)
                continue

            # print_info(f"全部{'x'*20}", winTitle, winProcessExe, pid)
            # _id = winTitle + winProcess #不好用,比如像telegram标题不断变化,自增数字,pid稳定好用
            _id = pid
            skipFlag = False
            skipObj = None
            sendFlag = False
            for ruleObj in rules:
                titleRegex = re.compile(ruleObj["title"].replace("\\", "\\\\"))
                titleMatch = titleRegex.match(winTitle)
                processRegex = re.compile(ruleObj["process"].replace("\\", "\\\\"))
                processMatch = processRegex.match(winProcessExe)
                if titleMatch and processMatch:
                    if appFlag != _id:
                        if ruleObj.get("skip"):
                            print_skip("matchSkip_catch", winProcessName)
                            skipFlag = True
                            skipObj = ruleObj
                            print("\n")
                            continue
                        print_info(f"----捕获", winTitle, winProcessExe, pid)
                        if not layerFlag == ruleObj["send"][1]:
                            send_hid_as_config("config.json", sendList=ruleObj["send"])
                            layerFlag = ruleObj["send"][1]
                            print_send(1, layerFlag=layerFlag, send=ruleObj["send"])
                        else:
                            print_send(0, layerFlag=layerFlag, send=ruleObj["send"])
                        appFlag = _id
                        sendFlag = True

                        run_ahk_script(
                            ahk_file_name,
                            ruleObj.get("ahk_code", []),
                            ruleObj.get("skip_ahk"),
                        )
                        print("\n")

            if skipFlag or not sendFlag:
                if appFlag != _id:
                    print_info(f"----漏网", winTitle, winProcessExe, pid)

                    if not layerFlag == escapList[1]:
                        send_hid_as_config("config.json", sendList=escapList)
                        layerFlag = escapList[1]
                        print_send(1, layerFlag=layerFlag, send=escapList)
                    else:
                        print_send(0, layerFlag=layerFlag, send=escapList)
                    appFlag = _id
                    if skipFlag:
                        run_ahk_script(
                            ahk_file_name,
                            skipObj.get("ahk_code", []),
                            skipObj.get("skip_ahk"),
                        )
                    else:
                        run_ahk_script(ahk_file_name, escapList_ahk, skip_escapList_ahk)
                    print("\n")


if __name__ == "__main__":
    fire.Fire(main)
