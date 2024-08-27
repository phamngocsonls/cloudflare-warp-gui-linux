#!/bin/bash -e
################################################################################
#
# Cloudflare WARP GUI for linux
#
# (C) 2022, Pham Ngoc Son <phamngocsonls@gmail.com> - Public Domain
# (C) 2024, Roberto A. Foglietta <roberto.foglietta@gmail.com> - 3-clause BSD
#
################################################################################

function filename() {
    echo "$@" | rev | cut -d/ -f1 | rev
}

if [ "${SUDO_USER+x}" == "" ]; then

echo
echo "WARNING: this script '$(filename $0)' requires root privileges"
echo
echo "         try again with 'sudo $0'"
echo

elif [ ! -r /etc/lsb-release ]; then

echo
echo "ERROR: this file /etc/lsb-release is missing, abort"
echo

else

source /etc/lsb-release

if [ "${DISTRIB_CODENAME+x}" == "" ]; then

echo
echo "ERROR: the DISTRIB_CODENAME is missing in /etc/lsb-release, abort"
echo

else ###########################################################################

set -e

cf_pkgurl="https://pkg.cloudflare.com"
kr_dpath="/usr/share/keyring"
kr_fname="$kr_dpath/cloudflare-warp-archive-keyring.gpg"

echo
echo "Downloading CloudFlare pgp keyring..."
echo
mkdir -p --mode=0755 $kr_dpath/
curl -fsSL $cf_pkgurl/cloudflare-main.gpg | gpg --yes --dearmor -o $kr_fname \
    && echo "done."

echo
echo "Updating packages database..."
echo
echo "deb [arch=amd64 signed-by=$kr_fname] $cf_pkgurl $DISTRIB_CODENAME main" \
    > /etc/apt/sources.list.d/cloudflare-client.list
apt-get update

for i in cloudflare-warp; do
    if apt-cache search $i | grep -qe "^$i "; then
        echo
        echo "Upgrading cloudflare-warp..."
        echo
        apt-get install --only-upgrade cloudflare-warp -y
    else
        echo
        echo "Installing cloudflare-warp..."
        echo
        apt-get install cloudflare-warp -y
    fi
done

echo
echo "CloudFlare application installed or updated, done."
echo

fi; fi #########################################################################

