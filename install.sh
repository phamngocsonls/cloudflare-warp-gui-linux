#!/bin/bash

echo
echo "Checking system requisites and dependencies..."
echo

################################################################################

if [ "$HOME" == "" ]; then
    if [ "$USER" != "" -a -d "/home/$USER/" ]; then
        export HOME="/home/$USER"
        echo
        echo "WARNING: enviroment variable \$HOME is not set"
        echo "         currently set to $HOME"
        echo
        read -sp "Press a key to continue"
        echo
    fi
fi

err=0

if [ "$HOME" == "" ]; then
    echo
    echo "ERROR: enviroment variable \$HOME is not set"
    echo
    err=1
fi

if ! which python3 | grep -q /usr/bin/python3; then
    echo
    echo "WARNING: /usr/bin/python3 is not in execution path"
    echo
    echo "HOW2FIX: sudo apt-get install python3 -y"
    echo
    err=1
fi

if ! which warp-cli >/dev/null; then
    echo
    echo "WARNING: warp-cli is not in execution path"
    echo
    echo "HOW2FIX: sudo apt-get install cloudflare-warp -y"
    echo
    err=1
fi

for i in python3-tk; do
    if ! apt-cache search $i | grep -qe "^$i "; then
        echo
        echo "WARNING: $i package is not installed"
        echo
        echo "HOW2FIX: sudo apt-get install $i -y"
        echo
        err=1
    fi
done

if ! which pip3 >/dev/null; then
    echo
    echo "WARNING: pip3 package is not installed"
    echo
    echo "HOW2FIX: sudo apt-get install pip3 -y"
    echo
    err=1
fi

for i in ipinfo requests; do
    if ! pip3 list | grep -we "^$i" >/dev/null; then
        echo
        echo "WARNING: pip3 $i module is not installed"
        echo
        echo "HOW2FIX: pip3 install $i"
        echo
        err=1
    fi
done

if [ $err -eq 0 ]; then ########################################################

echo "Creating folders and copying files..."
echo

mkdir -p $HOME/.local/share/applications/
mkdir -p $HOME/.local/share/icons/
mkdir -p $HOME/.local/bin/

sed -e "s,%HOME%,$HOME,g" warp-gui.desktop > $HOME/Desktop/warp-gui.desktop
cp -f appicon.png $HOME/.local/share/icons/warp-gui-app.png
cp -f $HOME/Desktop/warp-gui.desktop $HOME/.local/share/applications

cp -f warp-gui/warp-gui.py $HOME/.local/bin/
cp -f warp-gui/*.png $HOME/.local/bin
chmod a+x $HOME/.local/bin/warp-gui.py

echo "Disabling WARP taskbar applet..."
echo
systemctl --user disable warp-taskbar
systemctl --user stop warp-taskbar

echo "Installation done."
echo

fi #############################################################################


