import logging
import telegram.strings as tg_strings
from datetime import timedelta, datetime
from telegram.models import WMFTelegramBot
from db.models import WMFSQLDriver
from core.utils import timedelta_str, print_exception, get_env_mode, initialize_logger, get_curr_time_str
from wmf.models import WMFMachineStatConnector
if get_env_mode() == 'prod':
    from settings import prod as settings
else:
    from settings import test as settings


initialize_logger('daily_telegram_report.log')
logging.info('Started daily_telegram_report.py')
tg_conn = WMFTelegramBot()
try:
    db_conn = WMFSQLDriver()
    wm_conn = WMFMachineStatConnector()
    # tg_conn.send_message(f'Successfully connected to machine, part number is {wm_conn.part_number}', debug_mode=True)
    logging.info(f'Successfully connected to machine, part number is {wm_conn.part_number}')
    data = wm_conn.get_wmf_machine_info()
    time_worked = timedelta(minutes=settings.TELEGRAM_REPORT_INTERVAL_MINUTES)
    stoppage_time, wmf_error_time = timedelta(), timedelta()
    stoppage_count, wmf_error_count = 0, 0
    unsent_records = db_conn.get_unsent_records()
    for rec_id, error_code, start_time, end_time in unsent_records:
        if end_time:
            duration_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            time_worked -= duration_time
            if error_code == -1:
                stoppage_count += 1
                stoppage_time += duration_time
            else:
                wmf_error_count += 1
                wmf_error_time += duration_time
            db_conn.set_report_sent(rec_id)
    data['date_formed'] = get_curr_time_str()
    data['time_worked'] = timedelta_str(time_worked)
    data['wmf_error_time'] = timedelta_str(wmf_error_time)
    data['wmf_error_count'] = wmf_error_count
    data['stoppage_time'] = timedelta_str(stoppage_time)
    data['stoppage_count'] = stoppage_count

    last_record = db_conn.get_last_record()
    last_bev_count, last_cleaning_datetime = last_record[0], last_record[2]
    curr_bev_count = wm_conn.get_beverages_count()
    # tg_conn.send_message('Part_number %s: executed wm_conn.get_beverages_count(), received:\n\n%s' % (wm_conn.part_number, json.dumps(wm_conn.beverage_stats_raw)), debug_mode=True)
    if curr_bev_count:
        data['beverages_count'] = curr_bev_count - last_bev_count
        db_conn.save_last_record('beverages_count', curr_bev_count)
    else:
        data['beverages_count'] = tg_strings.NO_MACHINE_CONNECTION
    data['last_cleaning_datetime'] = last_cleaning_datetime

    tg_conn.send_message(tg_strings.DAILY_REPORT.format(**data))
    tg_conn.send_file('wmf.db', 'WMF PartNumber %s' % wm_conn.part_number, debug_mode=True)
    # beverage_list = wm_conn.get_beverages_list()
    # tg_conn.send_message('Executed wm_conn.get_beverages_list(), received:\n\n%s' % (json.dumps(beverage_list)))
    # tg_conn.send_message(json.dumps(wm_conn.send_wmf_request('getApiVersion')))
    # tg_conn.send_message(json.dumps(wm_conn.send_wmf_request('getDrinkList')))
    db_conn.close()
    wm_conn.close()
except Exception:
    exception_str = 'Part_number %s: daily_telegram_report.py exception occured:\n\n%s' % (wm_conn.part_number, print_exception())
    logging.error(exception_str)
    tg_conn.send_message(exception_str)

logging.info(f'Successfully finished daily_telegram_report.py, part number is {wm_conn.part_number}')
tg_conn.send_file('logs/daily_telegram_report.log', 'WMF PartNumber %s' % wm_conn.part_number, debug_mode=True)
