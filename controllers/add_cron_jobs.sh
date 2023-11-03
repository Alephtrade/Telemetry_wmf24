#!/bin/bash
croncmd="sh /root/wmf_1100_1500_5000_router/start_error_collector.sh >> start_error_collector.txt 2>&1"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/git_pull_autorestart.sh >> git_pull_autorestart.txt 2>&1"
cronjob="0 0 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/check_internet.sh >> check_internet.txt 2>&1"
cronjob="*/30 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_check_cleaning_and_rising.sh >> run_check_cleaning_and_rising.txt 2>&1"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_activity_beverages_sender.sh >> run_activity_beverages_sender.txt 2>&1"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /root/wmf_1100_1500_5000_router/run_activity_beverages_service_creator.sh >> run_activity_beverages_service_creator.txt 2>&1"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -
