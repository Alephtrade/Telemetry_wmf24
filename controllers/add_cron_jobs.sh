#!/bin/bash
croncmd="sh /var/www/Telemetry_wmf24/start_error_collector.sh >> /var/www/Telemetry_wmf24/start_error_collector.txt 2>&1"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/git_pull_autorestart.sh >> /var/www/Telemetry_wmf24/git_pull_autorestart.txt 2>&1"
cronjob="0 0 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/check_internet.sh >> /var/www/Telemetry_wmf24/check_internet.txt 2>&1"
cronjob="*/30 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/run_check_cleaning_and_rising.sh >> /var/www/Telemetry_wmf24/run_check_cleaning_and_rising.txt 2>&1"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/run_activity_beverages_sender.sh >> /var/www/Telemetry_wmf24/run_activity_beverages_sender.txt 2>&1"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/run_activity_beverages_service_creator.sh >> /var/www/Telemetry_wmf24/run_activity_beverages_service_creator.txt 2>&1"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -
