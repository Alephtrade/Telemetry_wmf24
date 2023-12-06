import json
import requests
import os
import sys
import logging
import linecache
from datetime import datetime, timedelta
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from logging.handlers import TimedRotatingFileHandler


def initialize_logger(filename='default.log'):
    os.makedirs(name='logs', exist_ok=True)
    log_file_name = os.path.join('logs', filename)
    handler = TimedRotatingFileHandler(filename=log_file_name, when='midnight', interval=1, backupCount=10)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(threadName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers={handler})


def get_logger(filename='default.log', logger_name='default'):
    logger = logging.getLogger(logger_name)
    os.makedirs(name='logs', exist_ok=True)
    log_file_name = os.path.join('logs', filename)
    handler = TimedRotatingFileHandler(filename=log_file_name, when='midnight', interval=1, backupCount=10)
    formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d [%(levelname)s] [%(threadName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def timedelta_str(delta):
    d = {'d': delta.days}
    d['h'], rem = divmod(delta.seconds, 3600)
    d['m'], d['s'] = divmod(rem, 60)
    if d['d'] > 0:
        return '{d} дней {h} часов {m} минут {s} секунд'.format(**d)
    else:
        return '{h} часов {m} минут {s} секунд'.format(**d)

def timedelta_int(delta):
    result = delta.days * 1 + delta.seconds
    return result


def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


def get_curr_time():
    return datetime.now()


def get_curr_time_str():
    return get_curr_time().strftime('%Y-%m-%d %H:%M:%S')


def get_next_date_formed(interval_minutes):
    next_time = datetime.now() + timedelta(minutes=interval_minutes)
    a = int(next_time.timestamp() // (interval_minutes * 60)) * (interval_minutes * 60) + 86400 - 54000 - 60
    return datetime.fromtimestamp(a)

def get_beverages_send_time(last_send_time):
    from controllers.db.models import WMFSQLDriver
    db_conn = WMFSQLDriver()
    initialize_logger('get_beverages_send_time.log')
    minutes_to_go = db_conn.get_exchange()
    next_time = datetime.strptime(str(last_send_time), '%Y-%m-%d %H:%M:%S')
    print(minutes_to_go)
    print(type(minutes_to_go))
    INTERVAL = db_conn.get_time_to_send_interval()
    if len(minutes_to_go) == 0 or minutes_to_go[0] is None:
        minutes_to_go = 0
    a = int(next_time.timestamp() // (60 * 60) * 60 * 60) + int(INTERVAL) * 60 * 60 + minutes_to_go * 60
    if a < int(datetime.now().timestamp()):
        a = int(int(datetime.now().timestamp()) // (60 * 60) * 60 * 60) + int(INTERVAL) * 60 * 60 + minutes_to_go * 60
    logging.info(f"created next time is:{a}")
    return datetime.fromtimestamp(a)
