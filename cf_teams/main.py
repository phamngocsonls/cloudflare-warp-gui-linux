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
        subprocess.Popen("yes yes | warp-cli register", shell=True)
        root.destroy()
        start_dir = "python3 " + dir_path + "/main.py"
        os.system(start_dir)

def get_acc_type():
    account = subprocess.getoutput("warp-cli account")
    if account.find("Team") > -1:
        return True
    else:
        return False

def acc_info():
    #Acc info
    if get_acc_type()==True:
        acc_label = Label(root, 
            text = "Zero Trust",
            fg = "Blue",
            font = ("Arial", 40, 'bold'))
        acc_label.pack(pady = 20)
    else:
        acc_label = Label(root, 
            text= "WARP",
            fg = "#FF5C33", 
            font = ("Arial", 40, 'bold'))
        acc_label.pack(pady = 20)

def cf_info():
    version = subprocess.getoutput("warp-cli --version")
    account = subprocess.getoutput("warp-cli account")
    status = subprocess.getoutput("warp-cli status")
    return version
    
def get_status():
    status = subprocess.getoutput("warp-cli status")
    if status.find("Disconnected") > -1:
        status = False
    elif status.find("Connected") > -1:
        status = True
    elif status.find("Connecting") > -1:
        status = "Connecting"
    return status

def get_ip():
    try:
        ipdis = ""
        ipdis = get('https://ifconfig.me/',timeout= 2.5).text
        details = handler.getDetails(ipdis).country
        return ipdis + " (" + details + ")"
    except:
    try:
            ipdis = get('https://ifconfig.me/',timeout= 2.5).text
            details = handler.getDetails(ipdis).country
        return ipdis + " (" + details + ")"
    except:
        return ipdis

def enroll():
    if get_acc_type() == True:
        subprocess.Popen("yes yes | warp-cli register", shell=True)
        slogan.config(image = logo)  
        subprocess.getoutput("warp-cli disconnect")

    else:
        organization = simpledialog.askstring(title="Organization",
                                  prompt="What's your Organization?:")
        new_command = "yes yes | warp-cli teams-enroll " + organization
        subprocess.Popen(new_command, shell=True)
        slogan.config(image = cflogo)
        subprocess.getoutput("warp-cli disconnect")

    on_button.config(image = off)
    
# create root windows
root = Tk()

menubar = Menu(root)
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
logo = PhotoImage(file = logo_dir)
appicon_dir = dir_path + "/appicon.png"
appicon = PhotoImage(file = appicon_dir)
logo = logo.subsample(10)
on = PhotoImage(file = on_dir)
on = on.subsample(3)
off = PhotoImage(file = off_dir)
off = off.subsample(3)
cflogo = PhotoImage(file = cflogo_dir)
cflogo = cflogo.subsample(2)

# root window title and dimension
root.title("WARP GUI for linux")
# Set geometry (widthxheight)
root.geometry('350x460')
root.iconphoto(False,appicon)


version = cf_info()
if version.find("not found") > -1:
    warp_version = "WARP not found"
else:
    warp_version = version
lbl = Label(root, text = warp_version)
lbl.grid()
lbl.place(relx=1.0, rely=1.0, anchor='se')


lbl = Label(root, text = "v0.1e")
lbl.grid()
lbl.place(relx=0.0, rely=1.0, anchor='sw')


# Keep track of the button state on/off
#global is_on
is_on = False


#status label
try:
    ip = ""
    ip = get('https://ip.seeip.org/',timeout= 2).text
    details = handler.getDetails(ip).country
    output = ip + " (" + details + ")"
except:
    output = ip
    pass



#Acc info
if get_acc_type()==True:
    acc_label = Label(root, 
        text = "Zero Trust",
        fg = "Blue",
        font = ("Arial", 40, 'bold'))
    acc_label.pack(pady = 20)
else:
    acc_label = Label(root, 
        text= "WARP",
        fg = "#FF5C33", 
        font = ("Arial", 40, 'bold'))
    acc_label.pack(pady = 20)


def change_ip_text():
    try:
        #time.sleep(2)
        info_label.config(text = get_ip(), 
                        fg = "Black")
    except:
        pass

#IP info`
info_label = Label(root, 
    text = output,
    fg = "black", 
    font = ("Arial", 20))
info_label.pack(pady = 20)

# Define our switch function
def switch():
    global is_on
    # Determin is on or switch

    if get_status()==True:
        status = subprocess.getoutput("warp-cli disconnect")
        time.sleep(0.5)
        if status == "Success":
            on_button.config(image = off)
    else:
        status = subprocess.getoutput("warp-cli connect")
        time.sleep(1)
        if get_status()==True:
            on_button.config(image = on)
        else:
            on_button.config(image = off)
            
    info_label.config(text = "", 
                fg = "Black")
    threading.Thread(target=change_ip_text).start()


# Create A Button
if get_status()==True:
    on_button = Button(root, image = on, bd = 0,
                    command = switch)
    on_button.pack(pady = 10)
else:
    on_button = Button(root, image = off, bd = 0,
                    command = switch)
    on_button.pack(pady = 10)

# Create Label
if get_status()==True:
    my_label = Label(root, 
        text = "Connected", 
        fg = "Black", 
        font = ("Arial", 15,'bold'))



else:
    my_label = Label(root, 
        text = "Disconnected", 
        fg = "Black", 
        font = ("Arial", 15,'bold'))

my_label.pack(padx=0, pady=0)

class TestThreading(object):
    def __init__(self, interval=1):
        subprocess.Popen("yes yes | warp-cli account", shell=True)
        self.interval = interval

        thread = threading.Thread(target=self.run, args=(acc_label,))
        thread.daemon = True
        thread.start()

    def run(self,acc_label):
        pre_latency = ""
        pre_loss = ""
        while True:
            status = subprocess.getoutput("warp-cli status")
            if(status.find("Status update: Connected")> -1):
                warp_stats = subprocess.getoutput("warp-cli warp-stats")
                stats_list = warp_stats.split()
                #up_time = stats_list[7]
                latency = stats_list[14]
                loss = stats_list[17]
                if pre_latency != latency or  pre_loss != loss:
                    try:
                        my_label_2.destroy()
                    except:
                        pass
                    my_label_2 = Label(root, 
                        text = "Latency: "+ latency + ", Loss: " + loss[:-1],
                        fg = "Black", 
                        font = ("Arial", 12))
                    my_label_2.pack(padx=0, pady=0)
                pre_latency = latency
                pre_loss = loss
 

            if get_acc_type()==True:
                acc_label.config(
                    text = "Zero Trust",
                    fg = "Blue",
                    font = ("Arial", 40, 'bold'))
                acc_label.pack(pady = 20)
            else:
                acc_label.config(
                    text= "WARP",
                    fg = "#FF5C33", 
                    font = ("Arial", 40, 'bold'))
                acc_label.pack(pady = 20)  

            status2 = get_status()
            if status2 == True:
                my_label.config(text = "Connected", fg = "Black")
            elif status2 == False:
                my_label.config(text = "Disconnected", fg = "Black")
            elif status2 == "Connecting":
                my_label.config(text = "Connecting...", fg = "Black")
            time.sleep(self.interval)


tr = TestThreading()
#logo
# Define Our Images

frame = Frame(root)
frame.pack(side=BOTTOM)
if (get_acc_type() == True):
    slogan = Button(frame, image = cflogo,
                    command=enroll)
    
elif (get_acc_type() == False):
    slogan = Button(frame, image = logo,
                    command=enroll)
slogan.pack(side=BOTTOM)


#update_button = Button(root, text="Update",
#                    command=update)
#update_button.place(x=270,y=410)     
# all widgets will be here
# Execute Tkinter
root.config(menu=menubar)
root.mainloop()
