cd ~/wmf_1100_1500_5000_router && git pull
if [ "$l" = "Already up to date." ]; then
    echo "restart not needed"
else
    echo "restart needed"
    kill -9 $(pgrep -f "python3 error_collector.py")
    python3 apply_migration.py
    sh /root/wmf_1100_1500_5000_router/start_error_collector.sh
fi
