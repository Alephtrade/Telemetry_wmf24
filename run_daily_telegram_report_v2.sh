#!/bin/bash
kill -9 $(pgrep -f "python3 daily_telegram_report_v2.py")
cd ~/wmf_1100_1500_5000_router
python3 daily_telegram_report_v2.py