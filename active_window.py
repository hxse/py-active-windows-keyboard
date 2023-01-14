import json
import re
import time
import win32gui, win32process, psutil
from send_hid import config as send_hid_as_config
import fire
from rich.theme import Theme
from rich.console import Console
import subprocess
import atexit

t = Theme(
    {
        "repeat_color": "#5f708b",
        "skip_color": "bold #fa7d00",
        "ahk_color_info": "#006eb1",
        "ahk_color_repeat": "#5f708b",
        "ahk_color_state_run": "green",
        "ahk_color_state_pause": "yellow",
        "ahk_color_state_exit": "red",
        "ahk_color_script": "#006eb1",
        "ahk_color_skip": "#5f708b",
    }
)

console = Console(theme=t)


def print_info(state, winTitle, winProcessExe, pid):
    console.print(f"[ahk_color_info]----windows info----[/ahk_color_info]")
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


def print_ahk(mode, ahk_code_list=None, ahk_code_text=None):
    global hidden_ahk_print, hidden_ahk_print_script
    if mode == "info":
        if not hidden_ahk_print:
            console.print(f"[ahk_color_info]---- ahk info ----[/ahk_color_info]")
    if mode == "repeat":
        if hidden_ahk_print_script:
            console.print(f"[ahk_color_repeat]no need repeat script[/ahk_color_repeat]")
        else:
            console.print(
                f"[ahk_color_repeat]no need repeat script\n[ahk_color_info]{ahk_code_text}[/ahk_color_info][/ahk_color_repeat]"
            )
    if mode == "script":
        if not hidden_ahk_print:
            if "Pause" in ahk_code_list:
                if hidden_ahk_print_script:
                    console.print(
                        f"[ahk_color_state_pause]pause ahk script...[/ahk_color_state_pause]"
                    )
                else:
                    console.print(
                        f"[ahk_color_state_pause]pause ahk script...[ahk_color_state_pause]\n[ahk_color_script]{ahk_code_text}[/ahk_color_script]"
                    )
            elif "exitApp" in ahk_code_list:
                if hidden_ahk_print_script:
                    console.print(
                        f"[ahk_color_state_exit]exit ahk script...[/ahk_color_state_exit]"
                    )
                else:
                    console.print(
                        f"[ahk_color_state_exit]exit ahk script...[/ahk_color_state_exit]\n[ahk_color_script]{ahk_code_text}[/ahk_color_script]"
                    )
            else:
                if hidden_ahk_print_script:
                    console.print(
                        f"[ahk_color_state_run]run ahk script...[/ahk_color_state_run]"
                    )
                else:
                    console.print(
                        f"[ahk_color_state_run]run ahk script...[/ahk_color_state_run]\n[ahk_color_script]{ahk_code_text}[/ahk_color_script]"
                    )
    if mode == "skip":
        console.print("[ahk_color_skip]不必启动ahk[/ahk_color_skip]")


def get_config_rules(path):
    global hidden_ahk_tray, hidden_ahk_print, hidden_ahk_print_script
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        rules = data.get("rules")
        escapList = data.get("escapList")
        ahk_file_name = data.get("ahk_file_name", "keyboard_mapping.ahk")
        hidden_ahk_tray = data.get("hidden_ahk_tray", True)
        hidden_ahk_print = data.get("hidden_ahk_print", False)
        hidden_ahk_print_script = data.get("hidden_ahk_print_script", True)
    return [
        rules,
        escapList,
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


def main(path="config.json", sleepTime=0.3):
    global ahkCodeFlag, hidden_ahk_tray, hidden_ahk_print, hidden_ahk_print_script
    [
        rules,
        escapList,
        ahk_file_name,
    ] = get_config_rules(path)

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
            skipObj = None
            for ruleObj in rules:
                titleRegex = re.compile(ruleObj["title"].replace("\\", "\\\\"))
                titleMatch = titleRegex.match(winTitle)
                processRegex = re.compile(ruleObj["process"].replace("\\", "\\\\"))
                processMatch = processRegex.match(winProcessExe)
                if titleMatch and processMatch:
                    if appFlag != _id:
                        if ruleObj.get("skip"):
                            print_skip("matchSkip", winProcessName)
                            skipObj = ruleObj
                            continue
                        print_info(f"----捕获", winTitle, winProcessExe, pid)
                        if not layerFlag == ruleObj["send"][1]:
                            send_hid_as_config("config.json", sendList=ruleObj["send"])
                            layerFlag = ruleObj["send"][1]
                            print_send(1, layerFlag=layerFlag, send=ruleObj["send"])
                        else:
                            print_send(0, layerFlag=layerFlag, send=ruleObj["send"])
                        appFlag = _id
                        run_ahk_script(
                            ahk_file_name,
                            ruleObj.get("ahk_code", []),
                            ruleObj.get("skip_ahk"),
                        )
                        print("\n")
                        break
                    break
            else:  # note this is for-loop else
                if appFlag != _id:
                    print_info(f"----漏网", winTitle, winProcessExe, pid)
                    if not layerFlag == escapList[1]:
                        send_hid_as_config("config.json", sendList=escapList)
                        layerFlag = escapList[1]
                        print_send(1, layerFlag=layerFlag, send=escapList)
                    else:
                        print_send(0, layerFlag=layerFlag, send=escapList)
                    appFlag = _id
                    if skipObj:
                        ruleObj = skipObj
                    run_ahk_script(
                        ahk_file_name,
                        ruleObj.get("ahk_code", []),
                        ruleObj.get("skip_ahk"),
                    )
                    print("\n")


if __name__ == "__main__":
    fire.Fire(main)
