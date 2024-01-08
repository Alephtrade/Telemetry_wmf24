#!/bin/bash
croncmd="sh /var/www/Telemetry_wmf24/controllers/machine_scan.sh >> /var/www/Telemetry_wmf24/migration.txt 2>&1"
cronjob="*/2 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/start_error_collector.sh >> /var/www/Telemetry_wmf24/start_error_collector.txt 2>&1"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/exchange_minutes.sh >> /var/www/Telemetry_wmf24/exchange_minutes.txt 2>&1"
cronjob="0 0 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/drink_list.sh >> /var/www/Telemetry_wmf24/drink_list.txt 2>&1"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/git_pull_autorestart.sh >> /var/www/Telemetry_wmf24/git_pull_autorestart.txt 2>&1"
cronjob="0 0 * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/check_internet.sh >> /var/www/Telemetry_wmf24/check_internet.txt 2>&1"
cronjob="*/30 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/run_check_cleaning_and_rising.sh >> /var/www/Telemetry_wmf24/run_check_cleaning_and_rising.txt 2>&1"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/run_activity_beverages_sender.sh >> /var/www/Telemetry_wmf24/run_activity_beverages_sender.txt 2>&1"
cronjob="* * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/run_activity_beverages_service_creator.sh 2>&1"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

croncmd="sh /var/www/Telemetry_wmf24/controllers/optimize_old_machine.sh >> /var/www/Telemetry_wmf24/optimize_old_machine.txt 2>&1"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -
