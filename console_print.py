#!/usr/bin/env python3
# coding: utf-8
from rich.theme import Theme
from rich.console import Console

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
            f"[bold green]{'-'*4}[/bold green][green]未检测到重复,可以发送 send: {send}[/green]"
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
    if mode == "matchSkip_catch":
        console.print(
            f"[skip_color]skip catch ==> match winProcessName: {winProcessName}[/skip_color]"
        )
    if mode == "matchSkip_escap":
        console.print(
            f"[skip_color]skip escap ==> match winProcessName: {winProcessName}[/skip_color]"
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
