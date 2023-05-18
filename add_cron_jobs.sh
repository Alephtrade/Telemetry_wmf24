croncmd="sh /root/wmf_1100_1500_5000_router/start_error_collector.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/git_pull_autorestart.sh"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_daily_telegram_report.sh"
cronjob="# 0 16 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_daily_telegram_report_v2.sh"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/check_internet.sh"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_check_machine_status.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_check_cleaning_state.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_clean_db.sh"
cronjob="3 22 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_send_debug_files.sh"
cronjob="# 3 2 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_pip_install.sh"
cronjob="# */10 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_send_ip_address.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

