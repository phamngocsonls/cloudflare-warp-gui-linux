## CloudFlare Graphical User Interface

A python TK graphic interface to manage the CloudFlare WARP+ or Team
Zero Trust virtual private network (VPN) connection which also offers
an advertising-free and safe browsing domain name system (DNS).

----

### Pre-requisites

```
sudo apt-get install pip3 python3 python3-tk -y
pip3 install ipinfo requests
```


### Direct execution

The `warp-gui/` folder contains all the stuff needs to run this application

```
python3 warp-gui/warp-gui.py
```

or make it executable and call it directly

```
chmod a+x warp-gui/warp-gui.py
./warp-gui/warp-gui.py
```

Hence the installtion script is checks, copying and creating a desktop icon/link


### Install script

```
bash install.sh
```

Then search for **CloudFlare** icon on the desktop and enable it for
running, using the mouse right button menu.

----

### Update GUI

pull from git repository the code and install it again

----

### Install or update warp-cli or add certificates

To install and update the `warp-cli` or add certificates, it requires the root
privileges:

```
sudo python3 warp-gui/warp-gui.py
```

Then use the menu to select your action to execute.

----

### Screenshots

This application allows to (dis)connect from both warp/team VPNs

![four stages screenshots](warp-gui-4-steps.png)

Icon on the taskbar changes with the connection status and the VPN type

<p><div align="center"><img src="warp-gui-4-icons.png" width="50%" height="50%" alt="four status icons"></div></p>

----

## License

The project and the installation script are under the very permissive **3-clauses
BSD license**. While the python application is licensed under **GNU General Public
License v2** because coding contributions are expected to be given back.

Some images are strictly related with CloudFlare trademark and related services
and cannot be relicensed. However, because this GUI is strictly and exclusively
related with `warp-cli` and their services, their integration within this project
can be considered a fair-use as intended in trademark and copyright common laws.

