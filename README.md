# WMF 1100, 1500, 5000 router software

**error_collector.py** collects errors from WMF Coffee machine in background and sends them every 5 minutes to wmf24.kz website

**daily_telegram_report.py** sends daily report to telegram channel about coffee machine

# How to manually update source code on router

1. Log into router via SSH using Putty
2. cd wmf_1100_1500_5000_router (you can type **cd wmf_1100** and press **Tab** for autocomplete, then **Enter**)
3. git pull

Note: **git_pull_autorestart.sh** script automatically does that

# How to enable test mode
Create config.env file in wmf_1100_1500_5000_router folder with this content:

```{"ENV_MODE": "test"}```

[Tasks sheet](https://docs.google.com/spreadsheets/d/1c5-ysAOZGqr1D_U2W0QwiUBQH72YvyVNEA_C10SGIEg/edit#gid=0)

# Warning
❗️❗️❗️**Do not update** wmf.db file in the repository❗️❗️❗️ **wmf_backup.db** is there just in case to restore the original file
