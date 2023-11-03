#!/bin/bash
IP="8.8.8.8" # Replace with the IP address you want to ping
COUNT=1 # Number of ping attempts
TIME=$(date)

if ping -c $COUNT $IP > /dev/null 2>&1; then
  echo "$TIME : Ping to $IP was successful."
else
  echo "$TIME : Ping to $IP failed."
  reboot
fi