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

# Import Module
from tkinter import *
import subprocess
import time
from requests import get
import tkinter.font as tkFont
import os 
import threading
import ipinfo
import os
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


def get_acc_type():
    account = subprocess.getoutput("warp-cli registration show")
    return (account.find("Team") > -1)


acc_type = "";

def acc_info_update():
    global acc_type
    acc_old = acc_type

    acc_type = get_acc_type()
    if acc_old == acc_type:
        return

    if acc_type == True:
        acc_label.config(text = "Zero Trust", fg = "Blue")
    else:
        acc_label.config(text = "WARP", fg = "Tomato")
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
    status = status.split("\n")[0]
    if status.find("Success") > -1:
        time.sleep(0.5)
        return get_status()
    status_err = status

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
    update_guiview()


# create root windows ##########################################################
root = Tk()

bgcolor = "GainsBoro"
menubar = Menu(root, bg = bgcolor)
helpmenu = Menu(menubar,tearoff=0)
#helpmenu.add_separator()
menubar.add_cascade(label="MENU",menu=helpmenu)
helpmenu.add_command(label="Update or Install", command=update)
helpmenu.add_command(label="Install Certificate", command=install_cert)

#button
logo_dir = dir_path + "/cf4teams.png"
on_dir = dir_path + "/on.png"
off_dir = dir_path + "/off.png"
cflogo_dir = dir_path + "/cflogo.png"
tmlogo = PhotoImage(file = logo_dir)
appicon_dir = dir_path + "/appicon.png"
appicon = PhotoImage(file = appicon_dir)
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

root.iconphoto(False,appicon)
root.config(bg = bgcolor)

lbl = Label(root, text = "GUI v0.4", fg = "DimGray", bg = bgcolor,
    font = ("Arial", 12), pady=10, padx=10)
lbl.grid()
lbl.place(relx=0.0, rely=1.0, anchor='sw')

#Acc info
acc_label = Label(root, text = "", bg = bgcolor, font = ("Arial", 40, 'bold'))
root.tr = threading.Thread(target=acc_info_update).start()
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
status_old = get_status()
on_button = Button(root, image = off, bd = 0, 
    activebackground = bgcolor, bg = bgcolor)
if status_old == "UP":
    on_button.config(image = on)

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
    info_label.config(text = get_ip())
    on_button.config(state = NORMAL)
    info_label.update()

def update_guiview():
    global status_old
    global status_err

    status_old = wait_status()

    if status_err != "":
        err_str = status_err.split("\n")
        err_str = err_str[0].split(".")
        err_str = "\n".join(err_str)
        stats_label.config(text = err_str, fg = "OrangeRed")
    elif status == "UP":
        on_button.config(image = on)
    elif status == "DN":
        on_button.config(image = off)
        stats_label.config(fg = "DimGray")
    else:
        return status

    on_button.update()
    stats_label.update()

    if status_old == "UP" or status_old == "DN":
        #root.tr = threading.Thread(target=change_ip_text).start()
        acc_info_update()
        change_ip_text()


# Define our switch function
def switch():
    global status_old
    global status_err

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
    update_guiview()

################################################################################

on_button.config(command = switch, state = DISABLED)
on_button.pack(pady = 0)

root.tr = threading.Thread(target=change_ip_text).start()

# Create Label
status_label = Label(root, text = "", fg = "Black", bg = bgcolor, font = ("Arial", 15))
status_label.pack(padx=0, pady=(0,10))

stats_label = Label(root, text = "", bg = bgcolor, font = ("Courier Condensed", 10))
stats_label.pack(padx=10, pady=(10,10))
old_warp_stats = warp_stats = ""

################################################################################

class TestThreading(object):

    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=(acc_label,))
        thread.daemon = True
        thread.start()

    def run(self,acc_label):
        global warp_stats

        while True:
            status = get_status()
            if status == "UP":
                old_warp_stats = warp_stats
                warp_stats = subprocess.getoutput("warp-cli tunnel stats")
                if warp_stats != "":
                    if warp_stats != old_warp_stats:
                        wsl = warp_stats.splitlines()
                        warp_stats = wsl[0] + "\n" + "\n".join(map(str, wsl[2:]))
                        stats_label.config(text = warp_stats, fg = "MidNightBlue")
                        old_warp_stats = warp_stats
                        stats_label.update()
                acc_info_update()
                status_label.config(text = "Connected", fg = "Blue",
                    font = ("Arial", 15, 'bold') )
                on_button.config(image = on)
            elif status == "DN":
                status_label.config(text = "Disconnected", fg = "DimGray",
                    font = ("Arial", 15, '') )
                on_button.config(image = off)
                stats_label.config(fg = "DimGray")
            elif status == "CN":
                status_label.config(text = "Connecting...", fg = "DimGray",
                    font = ("Arial", 15, 'italic') )
            status_label.update()
            stats_label.update()
            on_button.update()

            time.sleep(self.interval)


root.tr = TestThreading()

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
root.mainloop()
