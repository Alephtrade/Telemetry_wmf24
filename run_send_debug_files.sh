#!/bin/bash
kill -9 $(pgrep -f "python3 send_debug_files.py")
cd ~/wmf_1100_1500_5000_router
python3 send_debug_files.py