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
from requests import urllib3
import tkinter.font as tkFont
import os
import threading
import ipinfo
from tkinter import simpledialog
from functools import partial
from random import choice

dir_path = os.path.dirname(os.path.realpath(__file__))

registration_new_cmdline = "warp-cli --accept-tos registration new"
registration_new_cmdline +=" && warp-cli dns families malware"
registration_new_cmdline +=" && warp-cli set-mode warp+doh"

################################################################################

import requests
import socket

def inet_get_ipaddr(weburl="ifconfig.me", ipv6=False):
    weburl = weburl.split('/',1)
    if ipv6:
        # Resolve to an IPv6 address only (family=socket.AF_INET6)
        ip_info = socket.getaddrinfo(weburl[0], 80, family=socket.AF_INET6)
        # Construct the URL using the IPv6 address
        # IPv6 addresses should be enclosed in []
        ip_address = ip_info[0][4][0]
        url = f"http://[{ip_address}]/"
    else:
        # Resolve to an IPv4 address only (family=socket.AF_INET)
        ip_info = socket.getaddrinfo(weburl[0], 80, family=socket.AF_INET)
        # Construct the URL using the IPv4 address
        ip_address = ip_info[0][4][0]
        url = f"http://{ip_address}/"
    url+= weburl[1]

    if get_ipaddr.dbg:
        print("inet_get_ipaddr:", weburl[0], " + ", weburl[1], " = ", url)

    # Send the GET request with the Host header set to the original domain
    res = requests.get(url, headers={"Host": weburl[0]}, timeout=(0.8,1.0))
    return res.text.split('\n',1)[0] if res.status_code == 200 else ""

def ipv4_get_ipaddr(url="ifconfig.me"):
    return inet_get_ipaddr(url, 0)

def ipv6_get_ipaddr(url="ifconfig.me"):
    return inet_get_ipaddr(url, 1)

################################################################################

def inrun_wait(func, wait=0):
    if wait > 0:
        time.sleep(wait)
    elif func.inrun:
        while func.inrun:
            time.sleep(0.1)
    return 1

def get_status(wait=0):
    get_status.inrun = inrun_wait(get_status, wait)

    status = subprocess.getoutput("warp-cli status")
    if status.find("Success") == 0:
        return get_status(0.5)
    status = status.split("\n")[0]
    status_err = status.split(".")
    get_status.err = "\n".join(status_err)

    if status.find("Disconnected") > -1:
        get_status.reg = True
        status = "DN"
    elif status.find("Connected") > -1:
        get_status.reg = True
        status = "UP"
    elif status.find("Connecting") > -1:
        get_status.reg = True
        status = "CN"
    elif status.find("Registration Missing") > -1:
        get_status.reg = False
        status = "RGM"
    else:
        status = "ERR"

    if status != get_status.last:
        get_ipaddr.text = ""
        get_status.last = status

    get_status.inrun = 0
    return status

get_status.last = ""
get_status.err = ""
get_status.reg = True
get_status.inrun = 0


def update_guiview_by_menu(err_str, info_str):
    if err_str != "":
        err_str = err_str.split("\n")
        if err_str[0] == "Success":
            err_str = err_str[0] + ": " + info_str
        else:
            err_str = err_str[0].split(".")
            err_str = "\n".join(err_str)

    stats_label.config(text = err_str, fg = "OrangeRed")
    stats_label.update_idletasks()

    update_guiview(get_status(), 0)
    root.tr.resume()


def registration_delete():
    root.tr.pause()
    err_str = subprocess.getoutput("warp-cli registration delete")
    ipaddr_text_set()
    get_status.last = "RGM"
    update_guiview_by_menu(err_str, "registration delete")


def session_renew():
    global registration_new_cmdline

    root.tr.pause()

    if get_settings.warp_mode == 0 or get_settings.warp_dnsf == 0:
        get_settings()
    if get_status.last == "":
        get_status()

    oldval = get_status.last
    warp_mode_old = get_settings.warp_mode
    warp_dnsf_old = get_settings.warp_dnsf
    cmdline = registration_new_cmdline
    if oldval == "UP":
        cmdline += " && warp-cli connect"

    ipaddr_text_set()
    err_str = subprocess.getoutput("warp-cli registration delete; " + cmdline)
    if oldval == "UP":
        get_status.last = "CN"
    else:
        get_status.last = "DN"

    set_settings(warp_mode_old, warp_dnsf_old)
    update_guiview_by_menu(err_str, "WARP session renew")


def get_access():
    get_access.inrun = inrun_wait(get_access)

    account = subprocess.getoutput("warp-cli registration show")
    get_access.last = (account.find("Team") > -1)

    get_access.inrun = 0
    return get_access.last

get_access.last = ""
get_access.inrun = 0


def acc_info_update():
    status = get_status.last
    zerotrust = get_access()

    if zerotrust == True:
        acc_label.config(text = "Zero Trust", fg = "Blue")
    else:
        acc_label.config(text = "WARP", fg = "Tomato")
    acc_label.update_idletasks()

    if get_status.reg == False:
        slogan.config(image = cflogo)
    elif zerotrust == True:
        slogan.config(image = cflogo)
    else:
        slogan.config(image = tmlogo)
    slogan.update_idletasks()

    status_icon_update(status, zerotrust)


def status_icon_update(status=get_status.last, zerotrust=get_access.last):
    if zerotrust == True:
        if status == "UP":
            root.iconphoto(False,appicon_team)
        else:
            root.iconphoto(False,appicon_pass)
    else:
        if status == "UP":
            root.iconphoto(False,appicon_warp)
        else:
            root.iconphoto(False,appicon_pass)
    root.update_idletasks()


def cf_info():
    return subprocess.getoutput("warp-cli --version")


def force_get_ipaddr():
    get_ipaddr(True)


def get_ipaddr(force=False):
    global ipaddr_searching, ipaddr_errstring

    get_ipaddr.inrun = inrun_wait(get_ipaddr)

    if get_ipaddr.dbg:
        print("get_ipaddr(tries, force, ipv6):", get_ipaddr.tries, force,
            get_ipaddr.text.find("::") > 0)

    if force or get_ipaddr.text == "" or get_ipaddr.text == ipaddr_searching:
        get_ipaddr.tries = 0
    elif get_ipaddr.text == "\n" and get_ipaddr.tries < 2:
        pass
    elif get_ipaddr.tries < 2 \
    and urllib3.util.connection.HAS_IPV6 \
    and get_ipaddr.text.find("::") > 0:
        get_ipaddr.inrun = 0
        return get_ipaddr.text
    elif get_ipaddr.tries > 0:
        get_ipaddr.inrun = 0
        return get_ipaddr.text

    if get_ipaddr.dbg:
        print("get_ipaddr(try, ipaddr):", get_ipaddr.tries,
            get_ipaddr.text.replace("\n", " "))
    get_ipaddr.tries += 1

    url4 = choice(get_ipaddr.wurl4)
    url6 = choice(get_ipaddr.wurl6)
    if get_ipaddr.dbg:
        print("urls:", url4, url6)
    ipv4 = ipv6 = ""
    try:
        ipv4 = ipv4_get_ipaddr(url4)
        get_ipaddr.ipv4 = ipv4
    except Exception as e:
        if get_ipaddr.dbg:
            print("ERR> get ipv4(try, exception):", get_ipaddr.tries, str(e))
        get_ipaddr.ipv4 = ""
    try:
        ipv6 = ipv6_get_ipaddr(url6)
        get_ipaddr.ipv6 = ipv6
    except Exception as e:
        if get_ipaddr.dbg:
            print("ERR>  get ipv6(try, exception):", get_ipaddr.tries, str(e))
        get_ipaddr.ipv6 = ""

    if ipv4 + ipv6 == "":
        if get_ipaddr.tries > 1:
            root.after(3, force_get_ipaddr)
        get_ipaddr.inrun = 0
        #eturn "\n" + ipaddr_errstring
        return ipaddr_errstring

    country_city = get_country_city(get_ipaddr.ipv4)
    if country_city == "" and get_ipaddr.tries > 1:
        root.after(3, force_get_ipaddr)

    #get_ipaddr.text = country_city + "\n" + ipv4 + "\n" + ipv6
    get_ipaddr.text = ipv4 + " - " + country_city + "\n" \
        + (ipv6 if ipv6 else "-= ipv6 address unavailable =-")
    if get_ipaddr.dbg:
        print("get_ipaddr(try, ipstr):", get_ipaddr.tries,
            get_ipaddr.text.replace("\n", " "))

    get_ipaddr.inrun = 0
    return get_ipaddr.text

get_ipaddr.hadler_token = ""
get_ipaddr.handler = ipinfo.getHandler(get_ipaddr.hadler_token)
get_ipaddr.wurl4 = ['ifconfig.me/ip', 'api.ipify.org/',  'ip4.me/ip/']
get_ipaddr.wurl6 = ['ifconfig.me/ip', 'api6.ipify.org/', 'ip6only.me/ip/']
get_ipaddr.inrun = 0
get_ipaddr.text = ""
get_ipaddr.ipv4 = ""
get_ipaddr.ipv6 = ""
get_ipaddr.tries = 0
get_ipaddr.dbg = 0


def reset_country_city_dict():
    get_country_city.dict = dict()
    get_country_city.dict_reset = reset_country_city_dict.delay
#
# geolocalization caching delay value:
#   -N = perment cache (no reset)
#    0 = no any cache (disabled)
#   +N = last in seconds (temporary)
#
reset_country_city_dict.delay = 600


def get_country_city(ipaddr):
    global ipaddr_errstring

    if ipaddr == "":
        return ""

    if reset_country_city_dict.delay:
        try:
            return get_country_city.dict[ipaddr]
        except:
            pass

    try:
        # using the access_token from ipinfo
        details = get_ipaddr.handler.getDetails(ipaddr, timeout=(0.8,1.0))
        strn = details.city + " (" + details.country + ")"
        get_country_city.dict[ipaddr] = strn
        if get_country_city.dict_reset > 0:
            root.after(get_country_city.dict_reset, reset_country_city_dict)
            get_country_city.dict_reset = 0
        return strn
    except:
        return ipaddr_errstring

get_country_city.dict = dict()
get_country_city.dict_reset = reset_country_city_dict.delay


def enroll():
    global registration_new_cmdline

    subprocess.getoutput("warp-cli disconnect")
    try:
        if get_access.last == True or get_status.reg == False:
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
    subprocess.getoutput("warp-cli dns families " + filter)
    get_settings.warp_settings = ""


def set_mode(mode):
    subprocess.getoutput("warp-cli mode " + mode)
    get_settings.warp_settings = ""
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

# root window background color, title, dimension and position
root.title("WARP GUI")
root.geometry("360x480+120+90")
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
ipaddr_searching = "\n-=-.-=-.-=-.-=-"
ipaddr_errstring = "\n-= error or timeout =-"
ipaddr_label = Label(root, fg = "MidNightBlue", bg = bgcolor,
    font = ("Arial", 14), text = ipaddr_searching)
ipaddr_label.pack(pady = (20,10))

# Create A Button
on_button = Button(root, image = off, bd = 0, 
    activebackground = bgcolor, bg = bgcolor)
if get_status() == "UP":
    on_button.config(image = on)
else:
    ipaddr_label.config(fg = "DimGray")

threading.Thread(target=acc_info_update).start()

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
    ipaddr_text_set(get_ipaddr())
    on_button.config(state = NORMAL)
    ipaddr_label.update_idletasks()
    on_button.update_idletasks()


def auto_update_guiview(errlog=1):
    update_guiview(wait_status(), errlog)


def update_guiview(status, errlog=1):
    if update_guiview.inrun:
        return
    update_guiview.inrun = 1
    root.tr.pause()

    stats_err = 0
    if errlog and get_status.err != "":
        stats_label.config(text = get_status.err, fg = "OrangeRed")
        stats_err = 1

    if status == "UP":
        on_button.config(image = on)
    elif status != "CN":
        on_button.config(image = off)
        if errlog and stats_err == 0:
            stats_label.config(fg = "DimGray")

    on_button.update_idletasks()
    stats_label.update_idletasks()

    if status != "CN" and status != "DC":
        threading.Thread(target=acc_info_update).start()
        threading.Thread(target=change_ip_text).start()
        threading.Thread(target=get_settings).start()
        slide_update(status)
        time.sleep(0.1)

    root.tr.resume()
    update_guiview.inrun = 0

update_guiview.inrun = 0


def ipaddr_text_set(ipaddr_text=ipaddr_searching):
    if ipaddr_text == ipaddr_searching:
        ipaddr_label.config(fg = "DimGray")
    if get_status.last != "UP":
        ipaddr_label.config(fg = "DimGray")
    else:
        ipaddr_label.config(fg = "MidNightBlue")
    ipaddr_label.config(text = ipaddr_text)
    ipaddr_label.update_idletasks()


def slide_switch():
    if slide_switch.inrun:
        return
    slide_switch.inrun = 1

    root.tr.pause()
    on_button.config(state = DISABLED)
    on_button.update_idletasks()

    if get_status.last == "UP":
        get_status.last = "DC"
        status_label.config(text = "Disconnecting...", fg = "Dimgray",
            font = ("Arial", 15, 'italic') )
        retstr = subprocess.getoutput("warp-cli disconnect")
    elif get_status.last == "DN":
        get_status.last = "CN"
        status_label.config(text = "Connecting...", fg = "Dimgray",
            font = ("Arial", 15, 'italic') )
        retstr = subprocess.getoutput("warp-cli --accept-tos connect")
    status_label.update_idletasks()

    ipaddr_text_set()
    auto_update_guiview()

    root.tr.resume()
    slide_switch.inrun = 0

slide_switch.inrun = 0

################################################################################

on_button.config(command = slide_switch, state = DISABLED)
on_button.pack(pady = 0)

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
        on_button.update_idletasks()
        status_label.update_idletasks()


def stats_label_update():
    if stats_label_update.inrun:
        return
    stats_label_update.inrun = 1

    warp_stats = subprocess.getoutput("warp-cli tunnel stats")
    if warp_stats == "":
        pass
    elif warp_stats != stats_label_update.warp_stats_last:
        stats_label_update.warp_stats_last = warp_stats
        wsl = warp_stats.replace(';',' ')
        wsl = wsl.splitlines()
        wsl = wsl[0] + "\n" + "\n".join(map(str, wsl[2:]))
        stats_label.config(text = wsl, fg = "MidNightBlue")
        stats_label.update_idletasks()

    stats_label_update.inrun = 0

stats_label_update.warp_stats_last = ""
stats_label_update.inrun = 0


class TestThreading(object):

    def __init__(self, interval=1.0):
        self.skip = 0
        self.interval = interval
        self._event = threading.Event()
        thread = threading.Thread(target=self.run, args=(acc_label,))
        thread.daemon = True
        thread.start()

    def pause(self):
        self.skip = 1
        self._event.clear()

    def resume(self):
        self._event.set()
        self.skip = 0

    def run(self, acc_label):
        while True:
            if self.skip:
                time.sleep(self.interval/2)
                continue
            status = get_status()
            try:
                top = root.attributes('-topmost')
                top |= (root.focus_get() != None)
            except:
                top = 1
            if top == 1:
                if status == "UP":
                    stats_label_update()
                update_guiview(status, 0)
            else:
                stats_label.config(fg = "DimGray")
                status_icon_update(status, get_access())
            time.sleep(self.interval)

################################################################################

frame = Frame(root, bg = bgcolor)
frame.pack(side=BOTTOM, fill=X)

lbl_gui_ver = Label(frame, text = "GUI v0.8.0", fg = "DimGray", bg = bgcolor,
    font = ("Arial", 11, 'bold'), pady=10, padx=10)
lbl_gui_ver.place(relx=0.0, rely=1.0, anchor='sw')

slogan = Button(frame, image = "", command=enroll)
if get_status.reg == False:
    slogan.config(image = cflogo)
elif get_access.last == True:
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

def get_settings():
    global dnsf_types, dnsf_label, warp_label, warp_modes

    retstr = subprocess.getoutput(get_settings.warp_cmdline)
    if get_settings.warp_settings == retstr:
        return

    mode = retstr.find("Mode: ") + 6
    dnsf = retstr.find("Resolve via: ") + 13
    warp_mode_str = retstr[mode:].split()[0]
    warp_dnsf_str = retstr[dnsf:].split()[0].split(".")[0]
    get_settings.warp_settings = retstr
    
    try:
        get_settings.warp_mode = warp_label.index(warp_mode_str) + 1
    except:
        get_settings.warp_mode = 0

    try:
        get_settings.warp_dnsf = dnsf_label.index(warp_dnsf_str) + 1
    except:
        get_settings.warp_dnsf = 0

    warp_str = warp_modes[get_settings.warp_mode].split("_")[0]
    dnsf_str = dnsf_types[get_settings.warp_dnsf]
    lbl_setting.config(text = "mode:" + warp_str +  "\ndnsf:" + dnsf_str)
    lbl_setting.update_idletasks()

get_settings.warp_mode = 0
get_settings.warp_dnsf = 0
get_settings.warp_settings = ""
get_settings.warp_cmdline = 'warp-cli settings | grep --color=never -e "^("'


def settings_report():
    settings_report_cmdline = get_settings.warp_cmdline
    settings_report_cmdline +=' | sed -e "s/.*\\t//" -e "s/@/\\n\\t/"'
    report_str = subprocess.getoutput(settings_report_cmdline)
    print("\n\t-= SETTINGS REPORT =-\n\n" + report_str + "\n")


def set_settings(warp, dnsf):
    global dnsf_types, warp_modes
    set_dns_filter(dnsf_types[dnsf])
    set_mode(warp_modes[warp])

################################################################################

network_has_ipv6 = urllib3.util.connection.HAS_IPV6
# This line can enable or disable the IPv6 for 'requests' methods
urllib3.util.connection.HAS_IPV6 = True

print("\nrun.py path", dir_path,
      "\nipaddr url4", ", ".join(get_ipaddr.wurl4),
      "\nipaddr url6", ", ".join(get_ipaddr.wurl6),
      "\nnetwork has", ("IPv6" if network_has_ipv6 else "IPv4"),
       ("" if urllib3.util.connection.HAS_IPV6 else "disabled"),
      "\n")

root.config(menu=menubar)
root.tr = TestThreading()
root.update_idletasks()
root.mainloop()
