#!/bin/bash
kill -9 $(pgrep -f "python3 clean_db.py")
cd ~/wmf_1100_1500_5000_router
python3 clean_db.py