croncmd="sh /root/wmf_1100_1500_5000_router/start_error_collector.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/git_pull_autorestart.sh"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/check_internet.sh"
cronjob="*/30 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_check_machine_status.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_check_cleaning_state.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_check_cleaning_and_rising.sh"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_controller_machine_activity_creator.sh"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_controller_machine_activity_sender.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_send_ip_address.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_beverage_create_worker.sh"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_beverage_send_worker.sh"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_service_statistics_worker.sh"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -
