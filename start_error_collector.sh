#!/bin/bash
pid=$(pgrep -f "python3 error_collector.py")
echo $pid
if  [ -z $pid ]; then
  echo "Service not running, start running..."
  cd ~/wmf_1100_1500_5000_router
  python3 error_collector.py
else
  echo "Service already running."
fi