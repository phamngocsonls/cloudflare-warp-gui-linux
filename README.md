## CloudFlare WARP/TEAM GUI

A python TK graphic interface to manage the CloudFlare WARP / Team
Zero Trust virtual private network (VPN) connection which also offers
an advertising-free and safe browsing domain name system (DNS).

----

### Install script

```
sudo apt-get install python3-tk -y
python3 install.py
sudo cp -r cf_teams /usr/share/
sudo cp teams.sh /usr/bin/cf4teams
sudo chmod +x /usr/bin/cf4teams
```

Find "Cloudflare WARP" in app menu

----

### Update GUI

pull from git repository the code and install it again

----

### Update / Install / Add certificate

```
sudo /usr/bin/cf4teams
```

----

### Screenshots

![four stages screenshots](warp-gui-4-steps.png)

