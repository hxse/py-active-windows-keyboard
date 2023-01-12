import json
import re
import time
import win32gui, win32process, psutil
from colorama import Fore, Style
from send_hid import config as send_hid_as_config
import fire


def print_info(state, winTitle, winProcessExe, pid):
    _state = f"{Fore.BLUE}{state}"
    _pTitle = f"{Fore.BLUE}winTitle: {Fore.GREEN}{winTitle}"
    _pProcess = f"{Fore.BLUE}winProcess: {Fore.GREEN}{winProcessExe}"
    _pid = f"{Fore.BLUE}pid: {Fore.GREEN}{pid}{Style.RESET_ALL}"
    print(f"{_state}\n{_pTitle}\n{_pProcess}\n{_pid}")


def print_send(mode, layerFlag, send):
    if mode:
        print(f"{Fore.GREEN}send: {send} 已成功发送")
    else:
        print(f"{Fore.RED}send: {send} 已进入目标图层layerFlag: {layerFlag},不需要重复发送")


def get_config_rules(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        rules = data["rules"]
    return rules


def main(path="config.json", sleepTime=0.3):
    rules = get_config_rules(path)
    appFlag = -1
    layerFlag = -1
    while 1:
        # print(f"wait {sleepTime} second")
        time.sleep(sleepTime)
        window = win32gui.GetForegroundWindow()
        tid, pid = win32process.GetWindowThreadProcessId(window)
        winTitle = win32gui.GetWindowText(window)
        try:
            process = psutil.Process(pid)
            winProcessExe = process.exe()
            winProcessName = process.name()
        except Exception as e:
            print(
                f"{Fore.RED}报错, can't get process name winTitle: {winTitle} tid: {tid} pid: {pid} {e}"
            )
            continue

        # print_info(f"全部{'x'*20}", winTitle, winProcessExe, pid)
        # _id = winTitle + winProcess #不好用,比如像telegram标题不断变化,自增数字,pid稳定好用
        _id = pid
        for ruleObj in rules:
            titleRegex = re.compile(ruleObj["title"].replace("\\", "\\\\"))
            titleMatch = titleRegex.match(winTitle)
            processRegex = re.compile(ruleObj["process"].replace("\\", "\\\\"))
            processMatch = processRegex.match(winProcessExe)
            if titleMatch and processMatch:
                if appFlag != _id:
                    if ruleObj.get("skip"):
                        print(
                            f"{Fore.YELLOW}skip match winProcessName: {winProcessName}",
                        )
                        continue
                    print_info(f"捕获{'>'*20}", winTitle, winProcessExe, pid)
                    if not layerFlag == ruleObj["send"][1]:
                        send_hid_as_config("config.json", sendList=ruleObj["send"])
                        layerFlag = ruleObj["send"][1]
                        print_send(1, layerFlag=layerFlag, send=ruleObj["send"])
                    else:
                        print_send(0, layerFlag=layerFlag, send=ruleObj["send"])
                    appFlag = _id
                    print("\n")
                    break
                break
        else:  # note this is for-loop else
            if appFlag != _id:
                print_info(f"漏网{'-'*20}", winTitle, winProcessExe, pid)
                send = [1, 0]
                if not layerFlag == send[1]:
                    send_hid_as_config("config.json", sendList=send)
                    layerFlag = send[1]
                    print_send(1, layerFlag=layerFlag, send=send)
                else:
                    print_send(0, layerFlag=layerFlag, send=send)
                appFlag = _id
                print("\n")


if __name__ == "__main__":
    fire.Fire(main)
