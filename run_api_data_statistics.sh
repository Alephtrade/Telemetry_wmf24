#!/bin/bash
kill -9 $(pgrep -f "python3 api_data_statistics.py")
cd ~/wmf_1100_1500_5000_router
python3 controller_machine_activity.py