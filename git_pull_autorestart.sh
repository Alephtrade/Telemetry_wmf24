if [ "$(date +%H)" = "16" ] && [ "$(date +%M)" = "00" ]; then
  exit
fi
cd ~/wmf_1100_1500_5000_router
l=$(git pull | head -n 1)
if [ "$l" = "Already up to date." ]; then
    echo "restart not needed"
else
    echo "restart needed"
    kill -9 $(pgrep -f "python3 error_collector.py")
    pip3 install -r requirements.txt
    python3 apply_migration.py
    sh /root/wmf_1100_1500_5000_router/start_error_collector.sh
fi