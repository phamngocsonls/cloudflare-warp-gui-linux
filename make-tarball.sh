#!/bin/bash

function basename() {
    echo "$@" | rev | cut -d/ -f1 | rev
}

filename="$(basename $PWD).tar.gz"
scriptname="$(basename $0)"

exclopts='--exclude warp-gui-[0-9]-\*.png'
exclopts+=" --exclude $scriptname"
exclopts+=" --exclude $filename"
exclopts+=" --exclude README.md"

if [ "x$1" == "xfree" -o "x$1" == "x--free" ]; then
    echo
    echo "Creating an files archive for Debian..."
    echo
    exclopts+=' --exclude appicon\*.png --exclude orig'
else
    echo
    echo "Creating an files archive for Ubuntu..."
    echo
    echo "use option --free for Debian, instead"
    echo
fi

#echo "exclopts: $exclopts"
#echo

eval tar cvzf $filename $exclopts  *
echo
du -ks $filename
echo