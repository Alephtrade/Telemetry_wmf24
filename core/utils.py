import json
import os
import sys
import logging
import linecache
from datetime import datetime, timedelta
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


def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


def get_env_mode():
    try:
        with open('config.env') as f:
            return json.loads(f.read())['ENV_MODE']
    except Exception as e:
        return 'prod'


def get_curr_time():
    return datetime.now() + timedelta(hours=3)


def get_curr_time_str():
    return get_curr_time().strftime('%Y-%m-%d %H:%M:%S')


def get_part_number_local():
    try:
        with open('part_number.txt') as f:
            return f.read()
    except Exception:
        return ''


def get_next_date_formed(interval_minutes):
    next_time = datetime.now() + timedelta(minutes=interval_minutes)
    a = int(next_time.timestamp() // (interval_minutes * 60)) * (interval_minutes * 60) + 86400 - 54000 - 60
    return datetime.fromtimestamp(a)
