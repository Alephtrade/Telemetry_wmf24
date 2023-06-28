import requests
import json
import logging
import websocket
from datetime import timedelta, datetime
from db.models import WMFSQLDriver
import telegram.strings as tg_strings
from core.utils import timedelta_str, get_curr_time, initialize_logger, get_part_number_local, get_next_date_formed_v2
from wmf.models import WMFMachineStatConnector
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def getServiceStatistics():
    initialize_logger('response.txt')
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
        return ''
    logging.info(f"COFFEE_MACHINE: Received {part_number}")
    text_file = open("response.txt", "a")
    text_file.write(received_data)
    received_data = received_data.replace(']', '', 1)
    received_data = received_data + ', {"device_code" : ' + str(part_number) + '}]'
    # received_data.append({"device_id": part_number})
    # r = requests.post('https://wmf24.ru/api/servicestatistics', json=received_data)
    url = "https://wmf24.ru/api/servicestatistics"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=received_data)
    logging.info(f"servicestatistics: GET response: {response.text}")
    ws.close()
    return True

def getBeverageStatistics():
    initialize_logger('response.txt')
    ws = websocket.create_connection(WS_URL)
    request = json.dumps({'function': 'getBeverageStatistics'})
    logging.info(f"COFFEE_MACHINE: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    logging.info(f"COFFEE_MACHINE: Received {received_data}")
    try:
        with open('part_number.txt') as f:
            part_number = f.read()
    except Exception:
        return ''
    logging.info(f"COFFEE_MACHINE: Received {part_number}")
    text_file = open("response.txt", "a")
    text_file.write(received_data)
    received_data = received_data.replace(']', '', 1)
    received_data = received_data + ', {"device_code" : ' + str(part_number) + '}]'
    logging.info(f"beveragestatistics: Received {received_data}")
    summ = 0
    device_code = ""
    recipes = []
    date_to_send = get_next_date_formed_v2()
    date_formed = datetime.now() + timedelta(hours=3)
    for item in received_data:
        for k, item2 in item.items():
            if (k.startswith("device_code")):
                device_code = item2
            if (k.startswith("TotalCountRcp")):
                summ += item2
                recipes.append(item)


    #url = "https://wmf24.ru/api/beveragestatistics"
    #headers = {
    #    'Content-Type': 'application/json'
    #}
    #response = requests.request("POST", url, headers=headers, data=received_data)
    #logging.info(f"beveragestatistics: GET response: {response.text}")
    ws.close()
    return True

def send_report_info():
    global error_text_max_len
    time_worked = timedelta(minutes=settings.TELEGRAM_REPORT_INTERVAL_MINUTES)
    date_formed = get_curr_time()
    date_formed_str = date_formed.strftime('%Y-%m-%d %H:%M:%S')

    wm_conn = WMFMachineStatConnector()
    if not wm_conn.ws:
        return False
    logging.info(f'Successfully connected to machine, part number is {wm_conn.part_number}')
    data = wm_conn.get_wmf_machine_info()
    stoppage_time, wmf_error_time = timedelta(), timedelta()
    stoppage_count, wmf_error_count = 0, 0
    row_counter = 2
    unsent_records = db_conn.get_unsent_records()
    for rec_id, error_code, start_time, end_time, error_text in unsent_records:
        if end_time:
            error_text = error_text if error_text else ''
            duration_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time,
                                                                                                 '%Y-%m-%d %H:%M:%S')
            time_worked -= duration_time
            if error_code == -1:
                stoppage_count += 1
                stoppage_time += duration_time
            else:
                wmf_error_count += 1
                wmf_error_time += duration_time

    data['date_formed'] = date_formed_str
    data['worked_seconds'] = time_worked.total_seconds()
    data['time_worked'] = timedelta_str(time_worked)
    data['wmf_error_seconds'] = wmf_error_time.total_seconds()
    data['wmf_error_time'] = timedelta_str(wmf_error_time)
    data['wmf_error_count'] = wmf_error_count
    data['stoppage_seconds'] = stoppage_time.total_seconds()
    data['stoppage_time'] = timedelta_str(stoppage_time)
    data['stoppage_count'] = stoppage_count

    last_record = db_conn.get_last_record()
    last_bev_count, last_cleaning_datetime = last_record[0], last_record[2]
    curr_bev_count = wm_conn.get_beverages_count()
    if curr_bev_count:
        data['beverages_count'] = curr_bev_count - last_bev_count
    else:
        data['beverages_count'] = tg_strings.NO_MACHINE_CONNECTION
    data['last_cleaning_datetime'] = last_cleaning_datetime

    data['code'] = wm_conn.part_number

    url = "https://wmf24.ru/api/reportdata"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
    return response.text

