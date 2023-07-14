#!/bin/bash
IP="8.8.8.8" # Replace with the IP address you want to ping
COUNT=1 # Number of ping attempts

if ping -c $COUNT $IP > /dev/null 2>&1; then
  echo "Ping to $IP was successful."
else
  echo "Ping to $IP failed."
  #pip install -r requirements.txt && sh setup_openvpn.sh && /etc/init.d/network restart && reboot
fi