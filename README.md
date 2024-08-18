## CloudFlare WARP/TEAM GUI

A python TK graphic interface to manage the CloudFlare WARP / Team
Zero Trust virtual private network (VPN) connection which also offers
an advertising-free and safe browsing domain name system (DNS).

----

### Prerequisites

```
sudo apt-get install pip3 python3 python3-tk -y
pip3 install ipinfo requests
```

### Installation

```
bash install.sh
```

Then search for **CloudFlare** icon on the desktop and enable it for
running, using the mouse right button menu.

----

### Update GUI

pull from git repository the code and install it again

----

### Update or Install or Add certificate

```
sudo python3 warp-gui/main.py
```

Then use the menu to select your action to execute.

----

### Screenshots

This application allows to (dis)connect from both warp/team VPNs

![four stages screenshots](warp-gui-4-steps.png)

Icon on the taskbar changes with the connection status and the VPN type

<p><div align="center"><img src="warp-gui-4-icons.png" width="50%" height="50%" alt="four status icons"></div></p>

