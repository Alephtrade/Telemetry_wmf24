if [ "$(date +%H)" = "16" ] && [ "$(date +%M)" = "00" ]; then
  exit
fi
if ping -q -c 1 -W 1 google.com >/dev/null; then
  echo "The network is up"
else
  echo "The network is down"
  reboot
fi
