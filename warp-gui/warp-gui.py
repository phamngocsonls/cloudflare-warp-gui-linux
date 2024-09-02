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

# RAF, TODO
#
# pgrep -u $USER -alf warp-gui.py | grep -e "[0-9]* python.*[ /]warp-gui.py$"
# from tkinter import BOTH, NORMAL, ACTIVE, DISABLED
##  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# Import pip3 Module
from tkinter import *
from time import sleep
from os import getpid, path
from subprocess import getoutput
from requests import get as getUrl, urllib3
from threading import Thread, Event

filename = path.basename(__file__)
dir_path = path.dirname(path.realpath(__file__))

registration_new_cmdline = "warp-cli --accept-tos registration new"
registration_new_cmdline +=" && warp-cli dns families malware"
registration_new_cmdline +=" && warp-cli set-mode warp+doh"

ipaddr_errstring = "\n-= error or timeout =-"
ipaddr_searching = "-=-.-=-.-=-.-=-"

################################################################################

from socket import getaddrinfo, AF_INET, AF_INET6

def inet_get_ipaddr(weburl="ifconfig.me", ipv6=False):
    weburl = weburl.split('/',1)
    url = ""
    if ipv6:
        # Resolve to an IPv6 address only (family=AF_INET6)
        ip_info = getaddrinfo(weburl[0], 80, family=AF_INET6)
        # Construct the URL using the IPv6 address
        # IPv6 addresses should be enclosed in []
        ip_address = ip_info[0][4][0]
        url = f"http://[{ip_address}]/"
    else:
        # Resolve to an IPv4 address only (family=AF_INET)
        ip_info = getaddrinfo(weburl[0], 80, family=AF_INET)
        # Construct the URL using the IPv4 address
        ip_address = ip_info[0][4][0]
        url = f"http://{ip_address}/"

    if len(weburl) > 1:
        url+= weburl[1]

    if get_ipaddr.dbg:
        print("inet_get_ipaddr:", weburl, url)

    # Send the GET request with the Host header set to the original domain
    try:
        res = getUrl(url, headers={"Host": weburl[0]})
    except Exception as e:
        raise(e)

    if res.status_code != 200:
        print("WRN> inet_get_ipaddr() return code:", res.status_code)

    # RAF: return code 206 is partial content and should be discarded
    return res.text.split('\n',1)[0] if res.status_code != 206 else ""


def ipv4_get_ipaddr(url="ifconfig.me"):
    return inet_get_ipaddr(url, 0)

def ipv6_get_ipaddr(url="ifconfig.me"):
    return inet_get_ipaddr(url, 1)

################################################################################

from sys import _getframe
# for current func name, specify 0 or no argument.
# for name of caller of current func, specify 1.
# for name of caller of caller of current func, specify 2. etc.
func_name = lambda n=0: _getframe(n+1).f_code.co_name

# RAF, TODO
#
# This lock mechanism is based on a non atomic check-and-set opration in the
# future it can be changed using the 'with lock' paradigm and involving a
# threading.Lock(). However, there is no any race condition here to address but
# just a operational serialisation just for optimisation. Hence a flag is ok.
#
##  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
def inrun_wait_or_set(wait=0):
    func = eval(func_name(1))
    if wait > 0:
        sleep(wait)
    else:
        while func.inrun:
            sleep(0.10)
    func.inrun = 1


def inrun_reset(val=None):
    func = eval(func_name(1))
    func.inrun = 0
    return val
##  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

def get_status(wait=0):
    inrun_wait_or_set(wait)

    status = getoutput("warp-cli status")
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

    return inrun_reset(status)

get_status.last = ""
get_status.err = ""
get_status.reg = True
get_status.inrun = 0


def update_guiview_by_menu(err_str, info_str=""):
    if err_str != "":
        err_str = err_str.split("\n")
        if err_str[0] == "Success":
            err_str = err_str[0] + ": " + info_str
        else:
            err_str = err_str[0].split(".")
            err_str = "\n".join(err_str)
        if not info_str:
            info_str = err_str

    stats_label.config(text = err_str, fg = "OrangeRed")
    stats_label.update_idletasks()

    update_guiview(get_status(), 0)
    root.tr.resume()


def registration_delete():
    root.tr.pause()
    err_str = getoutput("warp-cli registration delete")
    ipaddr_text_set()
    get_status.last = "RGM"
    update_guiview_by_menu(err_str, "registration delete")


def information_refresh():
    root.tr.pause()
    ipaddr_text_set()
    get_status.last = ""
    reset_country_city_dict()
    update_guiview_by_menu("information refresh")


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
    err_str = getoutput("warp-cli registration delete; " + cmdline)
    if oldval == "UP":
        get_status.last = "CN"
    else:
        get_status.last = "DN"

    set_settings(warp_mode_old, warp_dnsf_old)
    update_guiview_by_menu(err_str, "WARP session renew")


def get_access():
    inrun_wait_or_set()

    account = getoutput("warp-cli registration show")
    get_access.last = (account.find("Team") > -1)

    return inrun_reset(get_access.last)

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
    return getoutput("warp-cli --version")


def force_get_ipaddr():
    ipaddr_text_set()
    get_ipaddr(True)


from random import choice
from ipinfo import getHandler

def get_ipaddr(force=False):
    global ipaddr_searching, ipaddr_errstring

    inrun_wait_or_set()

    if force or get_ipaddr.text == "" \
    or get_ipaddr.text.find(ipaddr_searching) > -1:
        get_ipaddr.tries = 0
    elif get_ipaddr.ipv4 or get_ipaddr.ipv6:
        return inrun_reset(get_ipaddr.text)

    if get_ipaddr.dbg:
        print("get_ipaddr(try, ipaddr):", get_ipaddr.tries,
            get_ipaddr.text.replace("\n", " "))

    get_ipaddr.tries += 1
    url4 = choice(get_ipaddr.wurl4)
    url6 = choice(get_ipaddr.wurl6)

    if get_ipaddr.dbg and get_ipaddr.tries == 1:
        print("ipv4 urls:", url4)
        print("ipv6 urls:", url6)

    ipv4 = ipv6 = ""
    try:
        ipv4 = ipv4_get_ipaddr(url4)
        get_ipaddr.ipv4 = ipv4
    except Exception as e:
        if 1 or get_ipaddr.dbg:
            print(f"ERR> ipv4_get_ipaddr({url4}) failed({get_ipaddr.tries}) -",
                str(e))
        get_ipaddr.ipv4 = ""
    try:
        ipv6 = ipv6_get_ipaddr(url6)
        get_ipaddr.ipv6 = ipv6
    except Exception as e:
        if 1 or get_ipaddr.dbg:
            print(f"ERR> ipv6_get_ipaddr({url6}) failed({get_ipaddr.tries}) -",
                str(e))
        get_ipaddr.ipv6 = ""

    if not ipv4 and not ipv6:
        return inrun_reset(ipaddr_searching + ipaddr_errstring)

    city = get_country_city(ipv4 if ipv4 else ipv6)
    get_ipaddr.city = city

    if not ipv4 or not ipv6 or not city:
        if get_ipaddr.tries > 1:
            root.after(3, force_get_ipaddr)

    get_ipaddr.text = ipv4 + (" - " if ipv4 else "") + city \
            + "\n" + (ipv6 if ipv6 else "-= ipv6 address unavailable =-")

    if get_ipaddr.dbg:
        print("get_ipaddr(try, ipstr):", get_ipaddr.tries,
            get_ipaddr.text.replace("\n", " "))

    return inrun_reset(get_ipaddr.text)

get_ipaddr.hadler_token = ""
get_ipaddr.handler = getHandler(get_ipaddr.hadler_token)
get_ipaddr.wurls = ['ifconfig.me/ip', 'icanhazip.com', 'myip.wtf/text', 'eth0.me']
get_ipaddr.wurl6 = ['api6.ipify.org/','ip6only.me/ip/'] + get_ipaddr.wurls
get_ipaddr.wurl4 = ['api.ipify.org/', 'ip4.me/ip/'] + get_ipaddr.wurls
get_ipaddr.inrun = 0
get_ipaddr.text = ""
get_ipaddr.ipv4 = ""
get_ipaddr.ipv6 = ""
get_ipaddr.city = ""
get_ipaddr.tries = 0
get_ipaddr.dbg = 0


def reset_country_city_dict():
    get_country_city.dict = dict()
    get_country_city.reset = get_country_city.delay


def get_country_city(ipaddr):
    global ipaddr_errstring

    if ipaddr == "":
        return ""

    if get_country_city.delay:
        try:
            city = get_country_city.dict[ipaddr]
            return city
        except:
            pass

    try:
        # using the access_token from ipinfo
        details = get_ipaddr.handler.getDetails(ipaddr)
    except:
        return ipaddr_errstring

    strn = details.city + " (" + details.country + ")"
    if get_country_city.reset > 0:
        root.after(get_country_city.delay, reset_country_city_dict)
        get_country_city.reset = 0
    get_country_city.dict[ipaddr] = strn
    
    if get_ipaddr.dbg:
        print("get_country_city.dict =", get_country_city.dict)

    return strn

get_country_city.dict = dict()
#
# geolocalization caching delay value:
#   -N = perment cache (no reset)
#    0 = no any cache (disabled)
#    N = cache reset (delayed)
#
get_country_city.delay = 600 # value in seconds
get_country_city.reset = get_country_city.delay


from tkinter import simpledialog

def enroll():
    global registration_new_cmdline

    getoutput("warp-cli disconnect")
    try:
        if get_access.last == True or get_status.reg == False:
            cmdline = registration_new_cmdline
            getoutput(cmdline)
            slogan.config(image = cflogo)
        else:
            organization = simpledialog.askstring(title="Organization",
                                      prompt="What's your Organization?:")
            if organization != "":
                new_command = "yes yes | warp-cli --accept-tos teams-enroll "
                getoutput(new_command + organization)
                slogan.config(image = tmlogo)
    except:
        pass
    auto_update_guiview()


def set_dns_filter(filter):
    getoutput("warp-cli dns families " + filter)
    get_settings.warp_settings = ""


def set_mode(mode):
    getoutput("warp-cli mode " + mode)
    get_settings.warp_settings = ""
    ipaddr_text_set()


def service_taskbar():
    cmdline = 'systemctl --user status warp-taskbar | sed -ne "s/Active: //p"'
    retstr = getoutput(cmdline)
    if retstr.find("inactive") > -1:
        cmdline = 'systemctl --user enable warp-taskbar;'
        cmdline+=' systemctl --user start warp-taskbar'
    else:
        cmdline = 'systemctl --user disable warp-taskbar;'
        cmdline+=' systemctl --user stop warp-taskbar'
    retstr = getoutput(cmdline)


def wait_status():
    while True:
        stats_label.config(text = "")

        status = get_status()
        if status != "CN" and status != "DC":
            return status
        sleep(0.10)

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
        Thread(target=acc_info_update).start()
        Thread(target=change_ip_text).start()
        Thread(target=get_settings).start()
        slide_update(status)
        sleep(0.10)

    root.tr.resume()
    update_guiview.inrun = 0

update_guiview.inrun = 0


def ipaddr_text_set(ipaddr_text=ipaddr_searching):
    if ipaddr_text.find(ipaddr_searching) > -1:
        ipaddr_text = "\n"+ipaddr_searching
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
        retstr = getoutput("warp-cli disconnect")
    elif get_status.last == "DN":
        get_status.last = "CN"
        status_label.config(text = "Connecting...", fg = "Dimgray",
            font = ("Arial", 15, 'italic') )
        retstr = getoutput("warp-cli --accept-tos connect")
    status_label.update_idletasks()

    ipaddr_text_set()
    auto_update_guiview()

    root.tr.resume()
    slide_switch.inrun = 0

slide_switch.inrun = 0


def kill_all_instances(filename=filename):
    if not filename:
        return

    cmd_kill_all = '"s/\([0-9]*\) python.*[ /]' + filename + '$/\\\\1/p"'
    cmd_kill_all = 'pgrep -u $USER -alf ' + filename + ' | sed -n ' \
                  + cmd_kill_all + " | xargs kill"
    ret_str = ""
    try:
        ret_str = getoutput(cmd_kill_all)
    except Exception as e:
        print(f"ERR> kill_all_instances(): {ret_str}\n\n", str(e))

    sleep(0.1)
    exit()

# create root windows ##########################################################

from functools import partial

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

menubar = Menu(root, bg = bgcolor, activeborderwidth = 4, relief=GROOVE, fg = "Black")
helpmenu = Menu(menubar, tearoff=1, font = "Arial 12", title="WARP GUI > MENU")
menubar.add_cascade(label="\u25BD MENU", compound="left", menu=helpmenu)
menubar.add_cascade(label="\u205D",    compound="left")
menubar.add_command(label="\u21F1 IP \u21F2", compound="left", command=force_get_ipaddr)

helpmenu.add_command(label=" \u204E WARP Session Renew ", command=session_renew)
helpmenu.add_command(label=" \u204E WARP Session Delete", command=registration_delete)
helpmenu.add_separator()
helpmenu.add_command(label="\u2058 DNS Filter: family",   command=partial(set_dns_filter, "full"))
helpmenu.add_command(label="\u2058 DNS Filter: malware",  command=partial(set_dns_filter, "malware"))
helpmenu.add_separator()
helpmenu.add_command(label=" \u2022 WARP Mode: doh",      command=partial(set_mode, "doh"))
helpmenu.add_command(label=" \u2022 WARP Mode: warp",     command=partial(set_mode, "warp"))
helpmenu.add_command(label=" \u2022 WARP Mode: warp+doh", command=partial(set_mode, "warp+doh"))
helpmenu.add_command(label=" \u2022 WARP Mode: tunnel",   command=partial(set_mode, "tunnel_only"))
helpmenu.add_command(label=" \u2022 WARP Mode: proxy",    command=partial(set_mode, "proxy"))
helpmenu.add_separator()
helpmenu.add_command(label="\u21C5 Service Taskbar Icon", command=service_taskbar)
helpmenu.add_command(label="\u21BA Refresh Information",  command=information_refresh)
helpmenu.add_separator()
helpmenu.add_command(label="\u24D8 GUI App Information",  command="")
helpmenu.add_command(label="\u24E7 GUI App Termination",  command=kill_all_instances)

# Access information
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

# IP information
ipaddr_label = Label(root, fg = "MidNightBlue", bg = bgcolor,
    font = ("Arial", 14), text = "\n" + ipaddr_searching)
ipaddr_label.pack(pady = (20,10))

# Create A Button
on_button = Button(root, image = off, bd = 0,
    activebackground = bgcolor, bg = bgcolor)
if get_status() == "UP":
    on_button.config(image = on)
else:
    ipaddr_label.config(fg = "DimGray")

Thread(target=acc_info_update).start()

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

    warp_stats = getoutput("warp-cli tunnel stats")
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
        self._event = Event()
        thread = Thread(target=self.run, args=(acc_label,))
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
                sleep(0.10)
                continue

            status = get_status()
            try:
                top = root.attributes('-topmost')
                top|= (root.focus_get() != None)
            except:
                top = 1
            if top == 1:
                if status == "UP":
                    stats_label_update()
                update_guiview(status, 0)
            else:
                stats_label.config(fg = "DimGray")
                status_icon_update(status, get_access())

            sleep(self.interval)

################################################################################

frame = Frame(root, bg = bgcolor)
frame.pack(side=BOTTOM, fill=X)

gui_pid_str = "pid:" + str(getpid())

lbl_pid_num = Label(frame, text = gui_pid_str, fg = "DimGray", bg = bgcolor,
    font = ("Arial", 10), pady=10, padx=10, justify=LEFT)
lbl_pid_num.place(relx=0.0, rely=1.0, anchor='sw')

gui_version_str = "GUI v0.8.3"

lbl_gui_ver = Label(frame, text = gui_version_str, fg = "DimGray", bg = bgcolor,
    font = ("Arial", 11, 'bold'), pady=0, padx=10, justify=LEFT)
lbl_gui_ver.place(relx=0.0, rely=0.67, anchor='sw')

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

    retstr = getoutput(get_settings.warp_cmdline)
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
    report_str = getoutput(settings_report_cmdline)
    print("\n\t-= SETTINGS REPORT =-\n\n" + report_str + "\n")


def set_settings(warp, dnsf):
    global dnsf_types, warp_modes
    set_dns_filter(dnsf_types[dnsf])
    set_mode(warp_modes[warp])

################################################################################

network_has_ipv6 = urllib3.util.connection.HAS_IPV6
# This line can enable or disable the IPv6 for 'requests' methods
urllib3.util.connection.HAS_IPV6 = True

print("\nthis script", filename,
      "\nrun.py path", dir_path,
      "\nipaddr url4", ", ".join(get_ipaddr.wurl4),
      "\nipaddr url6", ", ".join(get_ipaddr.wurl6),
      "\nnetwork has", ("IPv6" if network_has_ipv6 else "IPv4"),
       ("enabled" if urllib3.util.connection.HAS_IPV6 else "disabled"),
      "\n")

root.config(menu=menubar)
root.tr = TestThreading()
root.update_idletasks()
root.mainloop()
