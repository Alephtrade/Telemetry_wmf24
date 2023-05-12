import os
from telegram.models import WMFTelegramBot


tg_conn = WMFTelegramBot()
EXCEL_REPORT_FILENAME = 'error_report.xlsx'

if os.path.exists('machine_info.txt'):
    with open('machine_info.txt') as f:
        tg_conn.send_file(EXCEL_REPORT_FILENAME, f.read())
else:
    tg_conn.send_file(EXCEL_REPORT_FILENAME)
