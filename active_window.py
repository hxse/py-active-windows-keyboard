import json
import re
import time
import win32gui, win32process, psutil
from send_hid import config as send_hid_as_config
import fire
from rich.theme import Theme
from rich.console import Console

t = Theme({"repeat_color": "#5f708b", "skip_color": "bold #fa7d00"})

console = Console(theme=t)


def print_info(state, winTitle, winProcessExe, pid):
    console.print(f"[bold red]{state}[/bold red]")
    console.print(f"[bold blue]winTitle: [green]{winTitle}")
    console.print(f"[bold blue]winProcess: [green]{winProcessExe}")
    console.print(f"[bold blue]pid: [green]{pid}")


def print_send(mode, layerFlag, send):
    if mode:
        console.print(
            f"[bold green]{'-'*4}[/bold green][green]已成功发送 send: {send}[/green]"
        )
    else:
        console.print(
            f"[repeat_color]{'-'*4}不需要重复发送,已进入目标图层 layerFlag: {layerFlag} send: {send}[/repeat_color]"
        )


def print_error(mode, winTitle, tid, pid, e):
    if mode == "pidError":
        console.print(
            f"[bold red]报错, can't get process name winTitle: {winTitle} tid: {tid} pid: {pid} {e}[/bold red]"
        )


def print_skip(mode, winProcessName):
    if mode == "matchSkip":
        console.print(
            f"[skip_color]skip ==> match winProcessName: {winProcessName}[/skip_color]"
        )


def get_config_rules(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        rules = data["rules"]
    return rules


def main(path="config.json", sleepTime=0.3):
    rules = get_config_rules(path)
    appFlag = -1
    layerFlag = -1
    with console.status(
        "[bold green] Wait Windows...", spinner="bouncingBall"
    ) as status:
        while 1:
            time.sleep(sleepTime)
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
            for ruleObj in rules:
                titleRegex = re.compile(ruleObj["title"].replace("\\", "\\\\"))
                titleMatch = titleRegex.match(winTitle)
                processRegex = re.compile(ruleObj["process"].replace("\\", "\\\\"))
                processMatch = processRegex.match(winProcessExe)
                if titleMatch and processMatch:
                    if appFlag != _id:
                        if ruleObj.get("skip"):
                            print_skip("matchSkip", winProcessName)
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
