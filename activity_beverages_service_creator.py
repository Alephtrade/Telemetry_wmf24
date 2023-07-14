import websocket
import logging
import requests
import json
from datetime import timedelta, datetime
from db.models import WMFSQLDriver
from settings import prod as settings
from core.utils import timedelta_int, get_beverages_send_time, initialize_logger
from api.beverages import methods


WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def get_main_data_stat():
    initialize_logger('controller_machine_activity_creator.py.log')
    time_now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    last_send = db_conn.get_last_machine_activity()
    if last_send is None:
        now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
        date_to_send = get_beverages_send_time(now)
        db_conn.create_machine_activity(time_now, date_to_send)
    else:
        date_to_send = get_beverages_send_time(last_send[0])
        db_conn.create_machine_activity(time_now, date_to_send)
    stoppage_time, wmf_error_time, time_count_default = timedelta(), timedelta(), timedelta(seconds=3600)
    stoppage_count, wmf_error_count = 0, 0
    unsent_records = db_conn.get_error_records(time_now - timedelta(hours=1), time_now)
    for rec_id, error_code, start_time, end_time, error_text in unsent_records:
        date_error_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        if date_error_start < (time_now - timedelta(hours=1)) and end_time is None:
            time_count_default = 0
            stoppage_count = 0
            wmf_error_count = 0
            if error_code == -1:
                stoppage_time = timedelta(seconds=3600)
                wmf_error_time = timedelta()
            else:
                stoppage_time = timedelta()
                wmf_error_time = timedelta(seconds=3600)
            break
        elif date_error_start >= (time_now - timedelta(hours=1)) and end_time is not None:
            duration_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            if error_code == -1:
                stoppage_count += 1
            else:
                wmf_error_count += 1
        elif end_time is not None:
            duration_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - (time_now - timedelta(hours=1))
            if error_code == -1:
                stoppage_count += 1
            else:
                wmf_error_count += 1
        else:
            duration_time = time_now - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        time_count_default -= duration_time
        if error_code == -1:
            stoppage_time += duration_time
        else:
            wmf_error_time += duration_time


    wmf_error_time = timedelta_int(wmf_error_time)
    time_count_default = timedelta_int(time_count_default)
    stoppage_time = timedelta_int(stoppage_time)
    if(wmf_error_time > 3600):
        wmf_error_time = 3600
    if(time_count_default < 0):
        time_count_default = 0
    if(stoppage_time > 3600):
        stoppage_time = 3600

    db_conn.save_machine_activity("time_worked", time_count_default)
    db_conn.save_machine_activity("wmf_error_count", wmf_error_count)
    db_conn.save_machine_activity("wmf_error_time", wmf_error_time)
    db_conn.save_machine_activity("stoppage_count", stoppage_count)
    db_conn.save_machine_activity("stoppage_time", stoppage_time)

    logging.info(f'time_worked {time_count_default}, wmf_error_count {wmf_error_count}, wmf_error_time {wmf_error_time}, stoppage_count {stoppage_count}, stoppage_time: stoppage_time')
    return True


def get_service_statistics():
    initialize_logger('getServiceStatistics.log')
    ws = websocket.create_connection(WS_URL)
    request = json.dumps({'function': 'getServiceStatistics'})
    logging.info(f"COFFEE_MACHINE: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    logging.info(f"servicestatistics: Received {received_data}")
    try:
        with open('part_number.txt') as f:
            part_number = f.read()
    except Exception:
        logging.info(f'{part_number} is none')
    logging.info(f"COFFEE_MACHINE: Received {part_number}")
    text_file = open("response.txt", "a")
    text_file.write(received_data)
    received_data = received_data.replace(']', '', 1)
    received_data = received_data + ', {"device_code" : ' + str(part_number) + '}]'

    url = "https://wmf24.ru/api/servicestatistics"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=received_data)
    logging.info(f"servicestatistics: GET response: {response.text}")
    ws.close()
    return True


def are_need_to_create():
    initialize_logger('beveragestatistics.log')
    logging.info(f"beveragestatistics: Received Create start")
    last_send = db_conn.get_last_beverages_log()
    logging.info(f"{last_send}")
    if last_send is None:
        now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
        get = methods.Take_Create_Beverage_Statistics(now)
        logging.info(f" last_send unknown")
        logging.info(f"{get}")
    else:
        get = methods.Take_Create_Beverage_Statistics(last_send[3])
        logging.info(f"{get}")
    return True


are_need_to_create()
get_service_statistics()
get_main_data_stat()