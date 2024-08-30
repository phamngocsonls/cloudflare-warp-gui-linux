#!/usr/bin/python3
#
# (C) 2024, Roberto A. Foglietta <roberto.foglietta@gmail.com> - GPLv2
#
# to test:
#   python3 test3.py (click enter when the terminal will ask for kill the app)
#
# as DoS' PoC:
#   python3 test3.py & (enjoy your unresponsive Xorg-like system)
#

# Import pip3 Module
from tkinter import *
import subprocess
import time
import tkinter.font as tkFont
import os

def icon_window_hide(event=None):
    print(".")
    icon.iconify()

def icon_app_go_alive():
    print("*")
    icon.after(10,icon_update_icon)
    icon.after_idle(icon.iconify)
    icon.update()

def icon_update_icon():
    print("#")
    icon.after(1,icon_update_icon)
    icon.after_idle(icon.iconify)
    icon.update()

def on_focus_in(event=None):
    print("$")
    icon.iconify()

icon = Tk()

dir_path = os.path.dirname(os.path.realpath(__file__))
appicon_path = dir_path + "/warp-gui/orig/appicon-team.png"
appicon_init = PhotoImage(file = appicon_path)
bgcolor = "GainsBoro"

icon.title("")
icon.geometry('0x0+0+0')
icon.config(bg = bgcolor)
icon.resizable(False,False)
icon.iconphoto(True, appicon_init)

#icon.bind('<FocusIn>', icon_window_hide)
#icon.bind('<FocusOut>', icon_window_hide)
#icon.protocol("WM_TAKE_FOCUS", icon_window_hide)
icon.bind("<Map>", on_focus_in)
#icon.bind("<Unmap>", icon_window_hide)

icon.after_idle(icon_app_go_alive)
icon.mainloop()

