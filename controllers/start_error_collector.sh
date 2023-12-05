#!/bin/bash
pid=$(pgrep -f "python3 /var/www/Telemetry_wmf24/controllers/error_collector.py")
echo $pid
if  [ -z $pid ]; then
  echo "Service not running, start running..."
  cd /var/www/Telemetry_wmf24
  python3 /var/www/Telemetry_wmf24/controllers/error_collector.py
else
  kill $pid
  cd /var/www/Telemetry_wmf24
  python3 /var/www/Telemetry_wmf24/controllers/error_collector.py
  echo "Service already running."
fi