#!/bin/bash
rm /etc/config/openvpn
rm -r /root/openvpn
opkg update && opkg remove openvpn-mbedtls
opkg install openvpn
cat /root/wmf_1100_1500_5000_router/openvpn/etc/config/openvpn > /etc/config/openvpn
cd ~/wmf_1100_1500_5000_router
cp /root/wmf_1100_1500_5000_router/openvpn/wmf-russia.ovpn /etc/openvpn/wmf-russia.conf
chmod +x /etc/openvpn/wmf.conf
service openvpn start && service openvpn enable
