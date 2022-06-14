import os
import sys
from pathlib import Path
import subprocess

cur_path = sys.path[0]


os.system("pip3 install ipinfo")
os.system("cp {}/cf_teams/appicon.png ~/.local/share/icons/appicon.png".format(cur_path))

desktop_file = '{}/.local/share/applications/warp-gui.desktop'.format(Path.home())

file = open(desktop_file, 'w+')
file.write('''[Desktop Entry]
Name=Cloudflare WARP
Version=1.0
Comment=A gui app base on warp-cli for linux
Exec=bash /usr/bin/cf4teams
Icon=appicon
Terminal=false
Type=Application
'''.format(cur_path))
print('Desktop file created at "{}"'.format(desktop_file))
