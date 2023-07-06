#!/bin/bash
kill -9 $(pgrep -f "python3 check_cleaning_and_rising_state.py")
cd ~/wmf_1100_1500_5000_router
python3 check_cleaning_and_rising_state.py