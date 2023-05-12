#!/bin/bash
if [ "$(date +%H)" = "16" ] && [ "$(date +%M)" = "00" ]; then
  exit
fi
kill -9 $(pgrep -f "python3 check_cleaning_state.py")
cd ~/wmf_1100_1500_5000_router
python3 check_cleaning_state.py