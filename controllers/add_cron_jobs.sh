#!/bin/bash
croncmd="sh /var/www/Telemetry_wmf24/controllers/machine_scan.sh 2>&1"
cronjob="*/2 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/start_error_collector.sh 2>&1"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/exchange_minutes.sh 2>&1"
cronjob="0 0 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/drink_list.sh 2>&1"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/git_pull_autorestart.sh 2>&1"
cronjob="0 0 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/check_internet.sh 2>&1"
cronjob="*/30 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/run_check_cleaning_and_rising.sh 2>&1"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/run_activity_beverages_sender.sh 2>&1"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/run_activity_beverages_service_creator.sh 2>&1"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/optimize_old_machine.sh 2>&1"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/delete_old_data.sh 2>&1"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -
