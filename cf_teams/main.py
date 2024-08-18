#!/usr/bin/python3
################################################################################
#
# Cloudflare WARP GUI for linux
#
# (C) 2022, Pham Ngoc Son <phamngocsonls@gmail.com> - Public Domain
# (C) 2024, Roberto A. Foglietta <roberto.foglietta@gmail.com> - 3-clause BSD
#
################################################################################
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
#
################################################################################

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
from random import choice

#enter access_token from ipinfo
access_token = ""
handler = ipinfo.getHandler(access_token)
dir_path = os.path.dirname(os.path.realpath(__file__))

print(dir_path)


def install_cert():
    p = subprocess.Popen("sudo apt-get update; sudo apt-get install ca-certificates -y; curl -s -o /tmp/Cloudflare_CA.pem https://developers.cloudflare.com/cloudflare-one/static/documentation/connections/Cloudflare_CA.pem; cp /tmp/Cloudflare_CA.pem /usr/local/share/ca-certificates/Cloudflare_CA.crt; sudo update-ca-certificate; sudo apt install libnss3-tools; curl -s -o /tmp/cloudflare.crt https://developers.cloudflare.com/cloudflare-one/static/documentation/connections/Cloudflare_CA.crt; ls /home/ | awk '{print $1}' | xargs -i mkdir -p /home/{}/.pki/nssdb; ls /home/ | awk '{print $1}' | xargs -i certutil -d sql:/home/{}/.pki/nssdb -A -t 'C,,' -n 'Cloudflare-CA' -i /tmp/cloudflare.crt",shell=True)
    p.communicate()


def update():
    version = subprocess.getoutput("warp-cli --version")
    p = subprocess.Popen("curl https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg;echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ focal main' | sudo tee /etc/apt/sources.list.d/cloudflare-client.list; sudo apt update; sudo apt-get install cloudflare-warp -y; sudo apt-get install --only-upgrade cloudflare-warp -y",shell=True)
    p.communicate()
    time.sleep(3)
    new_version = subprocess.getoutput("warp-cli --version")

    if new_version != version:
        subprocess.getoutput("yes yes | warp-cli register")
        root.destroy()
        start_dir = "python3 " + dir_path + "/main.py"
        os.system(start_dir)


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
    status_old = "RGM"

    update_guiview_by_menu(err_str, "registration delete")


def session_renew():
    global status_old, update_thread_pause

    oldval = status_old
    cmdline = "warp-cli registration new"
    if oldval == "UP":
        cmdline = cmdline + " && warp-cli connect"
    update_thread_pause = True
    err_str = subprocess.getoutput("warp-cli registration delete; " + cmdline)
    if oldval == "UP":
        status_old = "CN"
    else:
        status_old = "DN"

    update_guiview_by_menu(err_str, "WARP session renew")


def get_acc_type():
    account = subprocess.getoutput("warp-cli registration show")
    return (account.find("Team") > -1)


acc_type = ""

def acc_info_update():
    global acc_type

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

    if registration_missing() == True:
        slogan.config(image = cflogo)
    elif acc_type == True:
        slogan.config(image = cflogo)
    else:
        slogan.config(image = tmlogo)
    slogan.update()


def cf_info():
    return subprocess.getoutput("warp-cli --version")


regstr_missng = False

def registration_missing():
    global regstr_missng
    return regstr_missng


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

def get_ip():
    global website, ipaddr

    if ipaddr != "":
        return ipaddr

    try:
        ipdis = get('https://' + choice(website), timeout=(0.5,1.0)).text
    except Exception as e:
        print("get ipaddr: ", str(e))
        return "-= error or timeout =-"

    try:
        details = handler.getDetails(ipdis, timeout=(0.5,1.0)).country
        ipaddr = ipdis + " (" + details + ")"
        return ipaddr
    except:
        return ipdis


def enroll():
    subprocess.getoutput("warp-cli disconnect")
    try:
        if acc_type == True or registration_missing() == True:
            cmdline = "warp-cli registration new"
            subprocess.getoutput(cmdline)
            slogan.config(image = cflogo)
        else:
            organization = simpledialog.askstring(title="Organization",
                                      prompt="What's your Organization?:")
            if organization != "":
                new_command = "yes yes | warp-cli teams-enroll " + organization
                subprocess.getoutput(new_command)
                slogan.config(image = tmlogo)
    except:
        pass
    auto_update_guiview()


# create root windows ##########################################################
root = Tk()

bgcolor = "GainsBoro"
menubar = Menu(root, bg = bgcolor)
helpmenu = Menu(menubar,tearoff=0)
menubar.add_cascade(label="MENU",menu=helpmenu)
helpmenu.add_command(label="Update or Install", command=update)
helpmenu.add_command(label="Install Certificate", command=install_cert)
helpmenu.add_separator()
helpmenu.add_command(label="Registration Delete", command=registration_delete)
helpmenu.add_command(label="WARP Session Renew ", command=session_renew)

#button
logo_dir = dir_path + "/cf4teams.png"
on_dir = dir_path + "/on.png"
off_dir = dir_path + "/off.png"
cflogo_dir = dir_path + "/cflogo.png"
tmlogo = PhotoImage(file = logo_dir)
appicon_path = dir_path + "/appicon-init.png"
appicon_init = PhotoImage(file = appicon_path)
appicon_path = dir_path + "/appicon-pass.png"
appicon_pass = PhotoImage(file = appicon_path)
appicon_path = dir_path + "/appicon-warp.png"
appicon_warp = PhotoImage(file = appicon_path)
appicon_path = dir_path + "/appicon-team.png"
appicon_team = PhotoImage(file = appicon_path)
tmlogo = tmlogo.subsample(10)
on = PhotoImage(file = on_dir)
on = on.subsample(3)
off = PhotoImage(file = off_dir)
off = off.subsample(3)
cflogo = PhotoImage(file = cflogo_dir)
cflogo = cflogo.subsample(2)

# root window title and dimension
root.title("WARP GUI")
# Set geometry (widthxheight)
root.geometry('360x480')
root.resizable(False,False)
root.iconphoto(True,appicon_init)
root.config(bg = bgcolor)

lbl = Label(root, text = "GUI v0.7.1", fg = "DimGray", bg = bgcolor,
    font = ("Arial", 12), pady=10, padx=10)
lbl.grid()
lbl.place(relx=0.0, rely=1.0, anchor='sw')

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
info_label = Label(root, fg = "MidNightBlue", bg = bgcolor,
    font = ("Arial", 14), text = "-=-.-=-.-=-.-=-")
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

    info_label.config(text = get_ip())
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
        slide_update(status)


# Define our switch function
def switch():
    global status_old

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
        retstr = subprocess.getoutput("warp-cli connect")

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
        self.status_oldval = ""
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
                if self.status_oldval != status:
                    self.status_oldval = status
                    update_guiview(status, 0)
            time.sleep(self.interval)

################################################################################

frame = Frame(root, bg = bgcolor)
frame.pack(side=BOTTOM)

slogan = Button(frame, image = "", command=enroll)
if registration_missing() == True:
    slogan.config(image = cflogo)
elif acc_type == True:
    slogan.config(image = cflogo)
else:
    slogan.config(image = tmlogo)
slogan.pack(side=BOTTOM, pady=10, padx=(10,10))

################################################################################

root.config(menu=menubar)
root.tr = TestThreading()
root.mainloop()
