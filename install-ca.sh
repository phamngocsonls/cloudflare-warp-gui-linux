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

else ###########################################################################

echo
echo "Updating packages database..."
echo
apt-get update
echo
echo "Installing ca-certificates..."
echo
apt-get install ca-certificates -y

# root access only clean tmp dir creation
tmpdir=$(mktemp -d)
chmod go-rx ${tmpdir}
rm -rf ${tmpdir}/*

echo
echo "Downloading Cloudflare CA..."
echo
url_path='developers.cloudflare.com/cloudflare-one/static/documentation/connections'
curl -fsSL https://$url_path/Cloudflare_CA.pem -o ${tmpdir}/Cloudflare_CA.pem \
    && echo "loudflare_CA.pem - done."
curl -fsSL https://$url_path/Cloudflare_CA.crt -o ${tmpdir}/cloudflare.crt \
    && echo "cloudflare.crt - done."

echo
echo "Updating ca-certificate..."
echo
mkdir -p /usr/local/share/ca-certificates
cp -f ${tmpdir}/Cloudflare_CA.pem /usr/local/share/ca-certificates/Cloudflare_CA.crt
update-ca-certificates

echo
echo "Installing libnss3-tools..."
echo
apt install libnss3-tools -y

echo
echo "Installing cloudflare.crt..."
echo
for i in $(grep '/home/.*sh' /etc/passwd | cut -d: -f1); do
    echo "Installing for user: $i..."
    echo
    mkdir -p /home/$i/.pki/nssdb
    certutil -d sql:/home/$i/.pki/nssdb -A -t 'C,,' -n 'Cloudflare-CA' \
        -i ${tmpdir}/cloudflare.crt
done

rm -rf ${tmpdir}/
echo "CloudFlare certificates installed or updated, done."
echo

fi #############################################################################
