#!/usr/bin/python3
################################################################################
#
# Cloudflare WARP GUI for linux
#
# (C) 2022, Pham Ngoc Son <phamngocsonls@gmail.com> - Public Domain
# (C) 2024, Roberto A. Foglietta <roberto.foglietta@gmail.com> - 3-clause BSD
# (C) 2024, Pham Ngoc Son <phamngocsonls@gmail.com> - 3-clause BSD
# (C) 2024, Roberto A. Foglietta <roberto.foglietta@gmail.com> - GPLv2
#
################################################################################
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
#
# NO WARRANTY ##################################################################
# 
# 11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY FOR
# THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN OTHERWISE
# STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE
# PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE DEFECTIVE,
# YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
#
# 12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL
# ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
# THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
# GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE
# OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR
# A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH
# HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
#
################################################################################
# To check the WARP connection: curl https://www.cloudflare.com/cdn-cgi/trace/

# Import pip3 Module
from tkinter import *
import subprocess
import time
from requests import get
import tkinter.font as tkFont
import os
import threading
import ipinfo
from tkinter import simpledialog
from functools import partial
from random import choice

#enter access_token from ipinfo
access_token = ""
handler = ipinfo.getHandler(access_token)
dir_path = os.path.dirname(os.path.realpath(__file__))

print(dir_path)

registration_new_cmdline = "warp-cli --accept-tos registration new"
registration_new_cmdline +=" && warp-cli dns families malware"
registration_new_cmdline +=" && warp-cli set-mode warp+doh"

################################################################################

def update_guiview_by_menu(err_str, info_str):
    global update_thread_pause

    if err_str != "":
        err_str = err_str.split("\n")
        if err_str[0] == "Success":
            err_str = err_str[0] + ": " + info_str
        else:
            err_str = err_str[0].split(".")
            err_str = "\n".join(err_str)

    stats_label.config(text = err_str, fg = "OrangeRed")
    stats_label.update()

    update_guiview(get_status(), 0)
    update_thread_pause = False


update_thread_pause = False

def registration_delete():
    global status_old, update_thread_pause

    update_thread_pause = True
    err_str = subprocess.getoutput("warp-cli registration delete")
    ipaddr_text_set()
    status_old = "RGM"

    update_guiview_by_menu(err_str, "registration delete")


def session_renew():
    global status_old, update_thread_pause, registration_new_cmdline
    global warp_mode, warp_dnsf

    update_thread_pause = True

    if warp_mode == 0 or warp_dnsf == 0:
        get_settings()
    if status_old == "":
        get_status()

    oldval = status_old
    warp_mode_old = warp_mode
    warp_dnsf_old = warp_dnsf
    cmdline = registration_new_cmdline
    if oldval == "UP":
        cmdline += " && warp-cli connect"

    ipaddr_text_set()
    err_str = subprocess.getoutput("warp-cli registration delete; " + cmdline)
    if oldval == "UP":
        status_old = "CN"
    else:
        status_old = "DN"

    set_settings(warp_mode_old, warp_dnsf_old)
    update_guiview_by_menu(err_str, "WARP session renew")


def get_acc_type():
    account = subprocess.getoutput("warp-cli registration show")
    return (account.find("Team") > -1)


acc_type = ""
regstr_missng = False

def acc_info_update():
    global acc_type, regstr_missng

    acc_type = get_acc_type()

    if acc_type == True:
        acc_label.config(text = "Zero Trust", fg = "Blue")
        if status_old == "UP":
            root.iconphoto(False,appicon_team)
        else:
            root.iconphoto(False,appicon_pass)
    else:
        acc_label.config(text = "WARP", fg = "Tomato")
        if status_old == "UP":
            root.iconphoto(False,appicon_warp)
        else:
            root.iconphoto(False,appicon_pass)
    acc_label.update()

    if regstr_missng == True:
        slogan.config(image = cflogo)
    elif acc_type == True:
        slogan.config(image = cflogo)
    else:
        slogan.config(image = tmlogo)
    slogan.update()


def cf_info():
    return subprocess.getoutput("warp-cli --version")


ipaddr = ""
status_err = ""
status_old = ""

def get_status():
    global status_err, regstr_missng, status_old, ipaddr

    status = subprocess.getoutput("warp-cli status")
    if status.find("Success") == 0:
        time.sleep(0.5)
        return get_status()
    status = status.split("\n")[0]
    status_err = status.split(".")
    status_err = "\n".join(status_err)

    if status.find("Disconnected") > -1:
        regstr_missng = False
        status = "DN"
    elif status.find("Connected") > -1:
        regstr_missng = False
        status = "UP"
    elif status.find("Connecting") > -1:
        regstr_missng = False
        status = "CN"
    elif status.find("Registration Missing") > -1:
        regstr_missng = True
        status = "RGM"
    else:
        status = "ERR"

    if status != status_old:
        ipaddr = ""
        status_old = status

    return status


website = ['ifconfig.me/ip', 'api.ipify.org/?format=text' ]

def get_ipaddr(force=False):
    global website, ipaddr

    if force == False:
        if ipaddr != "" and ipaddr[0] != '-':
            return ipaddr

    try:
        ipdis = get('https://' + choice(website), timeout=(0.5,1.0)).text
    except Exception as e:
        if False:
            print("get ipaddr: ", str(e))
        return "-= error or timeout =-"

    try:
        details = handler.getDetails(ipdis, timeout=(0.5,1.0)).country
        ipaddr = ipdis + " (" + details + ")"
        return ipaddr
    except:
        return ipdis


def enroll():
    global registration_new_cmdline, regstr_missng

    subprocess.getoutput("warp-cli disconnect")
    try:
        if acc_type == True or regstr_missng == True:
            cmdline = registration_new_cmdline
            subprocess.getoutput(cmdline)
            slogan.config(image = cflogo)
        else:
            organization = simpledialog.askstring(title="Organization",
                                      prompt="What's your Organization?:")
            if organization != "":
                new_command = "yes yes | warp-cli --accept-tos teams-enroll "
                subprocess.getoutput(new_command + organization)
                slogan.config(image = tmlogo)
    except:
        pass
    auto_update_guiview()


def set_dns_filter(filter):
    global warp_settings
    subprocess.getoutput("warp-cli dns families " + filter)
    warp_settings = ""


def set_mode(mode):
    global warp_settings
    subprocess.getoutput("warp-cli mode " + mode)
    warp_settings = ""
    ipaddr_text_set()


def service_taskbar():
    cmdline = 'systemctl --user status warp-taskbar | sed -ne "s/Active: //p"'
    retstr = subprocess.getoutput(cmdline)
    if retstr.find("inactive") > -1:
        cmdline = 'systemctl --user enable warp-taskbar;'
        cmdline+=' systemctl --user start warp-taskbar'
    else:
        cmdline = 'systemctl --user disable warp-taskbar;'
        cmdline+=' systemctl --user stop warp-taskbar'
    retstr = subprocess.getoutput(cmdline)

# create root windows ##########################################################

bgcolor = "GainsBoro"
root = Tk()

on_dir = dir_path + "/free/slide-on.png"
on = PhotoImage(file = on_dir)

off_dir = dir_path + "/free/slide-off.png"
off = PhotoImage(file = off_dir)

try:
    logo_dir = dir_path + "/orig/team-logo.png"
    tmlogo = PhotoImage(file = logo_dir)
except:
    logo_dir = dir_path + "/free/team-letter.png"
    tmlogo = PhotoImage(file = logo_dir)

try:
    cflogo_dir = dir_path + "/orig/warp-logo.png"
    cflogo = PhotoImage(file = cflogo_dir)
except:
    cflogo_dir = dir_path + "/free/warp-letter.png"
    cflogo = PhotoImage(file = cflogo_dir)

try:
    appicon_path = dir_path + "/orig/appicon-init.png"
    appicon_init = PhotoImage(file = appicon_path)
except:
    appicon_path = dir_path + "/free/appclou-init.png"
    appicon_init = PhotoImage(file = appicon_path)

try:
    appicon_path = dir_path + "/orig/appicon-pass.png"
    appicon_pass = PhotoImage(file = appicon_path)
except:
    appicon_path = dir_path + "/free/appclou-pass.png"
    appicon_pass = PhotoImage(file = appicon_path)   

try:
    appicon_path = dir_path + "/orig/appicon-warp.png"
    appicon_warp = PhotoImage(file = appicon_path)
except:
    appicon_path = dir_path + "/free/appclou-warp.png"
    appicon_warp = PhotoImage(file = appicon_path)

try:
    appicon_path = dir_path + "/orig/appicon-team.png"
    appicon_team = PhotoImage(file = appicon_path)
except:
    appicon_path = dir_path + "/free/appclou-team.png"
    appicon_team = PhotoImage(file = appicon_path)

# root window title and dimension
root.title("WARP GUI")
# Set geometry (widthxheight)
root.geometry('360x480')
root.resizable(False,False)
root.iconphoto(True,appicon_init)
root.config(bg = bgcolor)

menubar = Menu(root, bg = bgcolor, activeborderwidth = 4)
helpmenu = Menu(menubar, tearoff=1, relief=RAISED, font = "Arial 11")
menubar.add_cascade(label="MENU",menu=helpmenu)

helpmenu.add_command(label="Registration Delete", command=registration_delete)
helpmenu.add_command(label="WARP Session Renew ", command=session_renew)
helpmenu.add_command(label="WARP Service Taskbar",command=service_taskbar)
helpmenu.add_separator()
helpmenu.add_command(label="DNS Filter: family",  command=partial(set_dns_filter, "full"))
helpmenu.add_command(label="DNS Filter: malware", command=partial(set_dns_filter, "malware"))
helpmenu.add_separator()
helpmenu.add_command(label="WARP Mode: doh",      command=partial(set_mode, "doh"))
helpmenu.add_command(label="WARP Mode: warp",     command=partial(set_mode, "warp"))
helpmenu.add_command(label="WARP Mode: warp+doh", command=partial(set_mode, "warp+doh"))
helpmenu.add_command(label="WARP Mode: tunnel",   command=partial(set_mode, "tunnel_only"))
helpmenu.add_command(label="WARP Mode: proxy",    command=partial(set_mode, "proxy"))

#Acc info
acc_label = Label(root, text = "", bg = bgcolor, font = ("Arial", 40, 'bold'))
acc_label.pack(pady = 0)

version = cf_info()
if version.find("not found") > -1:
    warp_version = "WARP not found"
else:
    warp_version = version
warpver_label = Label(root, text = warp_version, fg = "DimGray",
    bg = bgcolor, font = ("Arial", 12))
warpver_label.pack(pady = (0,10))

#IP info
ipaddr_tocheck_waitstr = "-=-.-=-.-=-.-=-"
info_label = Label(root, fg = "MidNightBlue", bg = bgcolor,
    font = ("Arial", 14), text = ipaddr_tocheck_waitstr)
info_label.pack(pady = (30,10))

# Create A Button
on_button = Button(root, image = off, bd = 0, 
    activebackground = bgcolor, bg = bgcolor)
if get_status() == "UP":
    on_button.config(image = on)
else:
    info_label.config(fg = "DimGray")

root.tr = threading.Thread(target=acc_info_update).start()

################################################################################

def wait_status():
    status = get_status()
    if status == "CN":
        stats_label.config(text = "")
        while status == "CN":
            time.sleep(0.5)
            status = get_status()
        time.sleep(0.5)
        return get_status()
    return status


def change_ip_text():
    global status_old

    info_label.config(text = get_ipaddr())
    if status_old == "UP":
        info_label.config(fg = "MidNightBlue")
    else:
        info_label.config(fg = "DimGray")
    on_button.config(state = NORMAL)
    info_label.update()


def auto_update_guiview(errlog=1):
    update_guiview(wait_status(), errlog)


def update_guiview(status, errlog=1):
    global status_err

    stats_err = 0
    if errlog and status_err != "":
        stats_label.config(text = status_err, fg = "OrangeRed")
        stats_err = 1

    if status == "UP":
        on_button.config(image = on)
    elif status != "CN":
        on_button.config(image = off)
        if errlog and stats_err == 0:
            stats_label.config(fg = "DimGray")

    on_button.update()
    stats_label.update()

    if status != "CN" and status != "DC":
        root.tr = threading.Thread(target=acc_info_update).start()
        root.tr = threading.Thread(target=change_ip_text).start()
        root.tr = threading.Thread(target=get_settings).start()
        slide_update(status)


def ipaddr_text_set(ipaddr=ipaddr_tocheck_waitstr):
    ipaddr = ipaddr_tocheck_waitstr
    info_label.config(text=ipaddr)
    info_label.update()


# Define our switch function
def switch():
    global status_old, ipaddr, ipaddr_tocheck_waitstr

    on_button.config(state = DISABLED)

    if status_old == "UP":
        status_old = "DC"
        status_label.config(text = "Disconnecting...", fg = "Dimgray",
            font = ("Arial", 15, 'italic') )
        retstr = subprocess.getoutput("warp-cli disconnect")
    elif status_old == "DN":
        status_old = "CN"
        status_label.config(text = "Connecting...", fg = "Dimgray",
            font = ("Arial", 15, 'italic') )
        retstr = subprocess.getoutput("warp-cli --accept-tos connect")

    ipaddr_text_set()
    status_label.update()
    auto_update_guiview()

################################################################################

on_button.config(command = switch, state = DISABLED)
on_button.pack(pady = 0)

root.tr = threading.Thread(target=change_ip_text).start()

# Create Label
status_label = Label(root, text = "", fg = "Black", bg = bgcolor, font = ("Arial", 15))
status_label.pack(padx=0, pady=(0,10))

stats_label = Label(root, text = "", bg = bgcolor, font = ("Courier Condensed", 10))
stats_label.pack(padx=10, pady=(10,10))

################################################################################

def slide_update(status):
    change = 1

    if status == "UP":
        status_label.config(text = "Connected", fg = "Blue",
            font = ("Arial", 15, 'bold') )
        on_button.config(image = on)
    elif status == "DN":
        status_label.config(text = "Disconnected", fg = "DimGray",
            font = ("Arial", 15, '') )
        on_button.config(image = off)
        stats_label.config(fg = "DimGray")
    elif status == "RGM":
        status_label.config(text = "No registration", fg = "DimGray",
            font = ("Arial", 15, '') )
        on_button.config(image = off)
    elif status == "CN":
        status_label.config(text = "Connecting...", fg = "DimGray",
            font = ("Arial", 15, 'italic') )
    elif status == "DC":
        status_label.config(text = "Disconnecting...", fg = "DimGray",
            font = ("Arial", 15, 'italic') )
    else:
        change = 0

    if change:
        on_button.update()
        status_label.update()


old_warp_stats = warp_stats = ""

def stats_label_update():
    global warp_stats, old_warp_stats
        
    old_warp_stats = warp_stats
    warp_stats = subprocess.getoutput("warp-cli tunnel stats")
    if warp_stats == "":
        warp_stats = old_warp_stats
    elif warp_stats != old_warp_stats:
        old_warp_stats = warp_stats
        wsl = warp_stats.splitlines()
        wsl = wsl[0] + "\n" + "\n".join(map(str, wsl[2:]))
        stats_label.config(text = wsl, fg = "MidNightBlue")
        stats_label.update()


class TestThreading(object):

    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=(acc_label,))
        thread.daemon = True
        thread.start()

    def run(self,acc_label):
        while True:
            if update_thread_pause == False:
                status = get_status()
                if status == "UP":
                    stats_label_update()
                update_guiview(status, 0)
            time.sleep(self.interval)

################################################################################

frame = Frame(root, bg = bgcolor)
frame.pack(side=BOTTOM, fill=X)

lbl_gui_ver = Label(frame, text = "GUI v0.7.8", fg = "DimGray", bg = bgcolor,
    font = ("Arial", 11, 'bold'), pady=10, padx=10)
lbl_gui_ver.place(relx=0.0, rely=1.0, anchor='sw')

slogan = Button(frame, image = "", command=enroll)
if regstr_missng == True:
    slogan.config(image = cflogo)
elif acc_type == True:
    slogan.config(image = cflogo)
else:
    slogan.config(image = tmlogo)
slogan.pack(side=BOTTOM, pady=10, padx=(10,10))

lbl_setting = Label(frame, text = "mode: - - - -\ndnsf: - - - -", fg = "Black",
    bg = bgcolor, font =  ("Courier", 10), pady=10, padx=10, justify=LEFT)
lbl_setting.place(relx=1.0, rely=1.0, anchor='se')

################################################################################

warp_modes = ['unknown', 'warp', 'doh',          'warp+doh',
       'dot',        'warp+dot',           'proxy',     'tunnel_only']
warp_label = [           'Warp', 'DnsOverHttps', 'WarpWithDnsOverHttps',
       'DnsOverTls', 'WarpWithDnsOverTls', 'WarpProxy', 'TunnelOnly' ]
dnsf_types = ['unknown', 'full',   'malware',  'off']
dnsf_label = [           'family', 'security', 'cloudflare-dns' ]

warp_mode = 0
warp_dnsf = 0
warp_settings = ""
warp_settings_cmdline = 'warp-cli settings | grep --color=never -e "^("'

def get_settings():
    global warp_mode, warp_dnsf, warp_settings, warp_settings_cmdline
    global dnsf_types, dnsf_label, warp_label, warp_modes

    retstr = subprocess.getoutput(warp_settings_cmdline)
    if warp_settings == retstr:
        return

    warp_settings = retstr
    mode = warp_settings.find("Mode: ") + 6
    dnsf = warp_settings.find("Resolve via: ") + 13
    warp_mode_str = warp_settings[mode:].split()[0]
    warp_dnsf_str = warp_settings[dnsf:].split()[0].split(".")[0]

    try:
        warp_mode = warp_label.index(warp_mode_str) + 1
    except:
        warp_mode = 0

    try:
        warp_dnsf = dnsf_label.index(warp_dnsf_str) + 1
    except:
        warp_dnsf = 0

    lbl_setting.config(text = "mode:" + warp_modes[warp_mode].split("_")[0] +
                            "\ndnsf:" + dnsf_types[warp_dnsf])
    lbl_setting.update()


def settings_report():
    global warp_settings_cmdline

    settings_report_cmdline = warp_settings_cmdline
    settings_report_cmdline +=' | sed -e "s/.*\\t//" -e "s/@/\\n\\t/"'
    report_str = subprocess.getoutput(settings_report_cmdline)
    print("\n\t-= SETTINGS REPORT =-\n\n" + report_str + "\n")


def set_settings(warp, dnsf):
    global dnsf_types, warp_modes
    set_dns_filter(dnsf_types[dnsf])
    set_mode(warp_modes[warp])

root.config(menu=menubar)
root.tr = TestThreading()
root.mainloop()
