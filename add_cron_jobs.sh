croncmd="sh /root/wmf_1100_1500_5000_router_ru/start_error_collector.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/git_pull_autorestart.sh"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/run_daily_telegram_report.sh"
cronjob="# 0 16 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/run_daily_telegram_report_v2.sh"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/check_internet.sh"
cronjob="# */5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/run_check_machine_status.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/run_check_cleaning_state.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/run_clean_db.sh"
cronjob="3 22 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/run_send_debug_files.sh"
cronjob="# 3 2 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/run_pip_install.sh"
cronjob="# */10 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/run_send_ip_address.sh"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/setup_openvpn.sh"
cronjob="# 5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router_ru/ovpn_enable.sh"
cronjob="* * * 1 * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

