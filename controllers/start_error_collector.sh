#!/bin/bash
pid=$(pgrep -f "python3 /root/wmf_1100_1500_5000_router/error_collector.py")
echo $pid
if  [ -z $pid ]; then
  echo "Service not running, start running..."
  cd /var/www/Telemetry_wmf24
  python3 /var/www/Telemetry_wmf24/controllers/error_collector.py
else
  echo "Service already running."
fi