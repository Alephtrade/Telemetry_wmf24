from telegram.models import WMFTelegramBot
from core.utils import get_part_number_local
tg_conn = WMFTelegramBot()

part_number = get_part_number_local()
tg_conn.send_file('wmf.db', 'WMF PartNumber %s' % part_number, debug_mode=True)
# tg_conn.send_file('logs/daily_telegram_report_v2.log', 'WMF PartNumber %s' % part_number, debug_mode=True)
# tg_conn.send_file('logs/error_collector.log', 'WMF PartNumber %s' % part_number, debug_mode=True)
# tg_conn.send_file('error_report.xlsx', 'WMF PartNumber %s' % part_number, debug_mode=True)
