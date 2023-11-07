import websocket
import logging
import requests
import json
import ast
import socket
from datetime import timedelta, datetime, time
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.core.utils import timedelta_int, get_beverages_send_time, initialize_logger
from controllers.api.beverages import methods
from controllers.wmf.models import WMFMachineStatConnector


WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def beverages_send_worker():
    initialize_logger('beverages_send_worker.py.log')
    k = []
    time_to_send = None
    receive_data = db_conn.get_not_sended_beverages_log()
    if(receive_data == []):
        logging.info(f'NO DATA')
    else:
        for item in receive_data:
            logging.info(f'loop')
            time_to_send = item[2]
            k.append({"device_code": item[0]})
            k.append({"summ": item[1]})
            k.append({"time_to_send": item[2]})
            k.append({"time_fact_send": item[3]})
            k.append({"date_formed": item[4]})
            data_info = ast.literal_eval(str(item[5]))
            record_id = item[6]
            for item_info in data_info:
                k.append(item_info)
            next_time = datetime.strptime(time_to_send, '%Y-%m-%d %H:%M:%S')
            if datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())) > next_time:
                methods.Send_Statistics(json.dumps(k), record_id)
                logging.info(f'Send_Statistics db id - {record_id}')
            else:
                logging.info(f'wrong time to_sent - {next_time}')
    return True


def controller_data_statistics_sender():
    initialize_logger('controller_data_statistics_sender.py.log')
    now_of_hour = str(datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())))
    data_for_request = []
    try:
        with open('/root/wmf_1100_1500_5000_router/part_number.txt') as f:
            part_number = f.read()
    except Exception:
        wm_conn = WMFMachineStatConnector()
        part_number = wm_conn.get_part_number()
    data_main_stat = db_conn.get_data_statistics_to_send()
    if data_main_stat is not None:
        for item in data_main_stat:
            if datetime.strptime(item[6], '%Y-%m-%d %H:%M:%S') < datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())):
                data_for_request.append({"time_worked": item[0]})
                data_for_request.append({"wmf_error_count": item[1]})
                data_for_request.append({"wmf_error_time": item[2]})
                data_for_request.append({"stoppage_count": item[3]})
                data_for_request.append({"stoppage_time": item[4]})
                data_for_request.append({"date_formed": item[5]})
                data_for_request.append({"time_to_send": item[6]})
                data_for_request.append({"time_fact_send": item[7]})
                data_for_request.append({"is_sent": item[8]})
                data_for_request.append({"code": part_number})
                url = "https://wmf24.ru/api/machineactivity"
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=json.dumps(data_for_request))
                logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
                print(item[9])
                db_conn.save_status_data_statistics(item[9], "is_sent", "1")
                db_conn.save_status_data_statistics(item[9], "time_fact_send", now_of_hour)
                logging.info(f'{datetime.now()} {response.text}')
            logging.info(f'Done')
    logging.info(f'nothing to send')
    return True

def send_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    data = {}

    try:
        with open('/root/wmf_1100_1500_5000_router/ip_address.json') as f:
            data = json.load(f)
    except FileNotFoundError:
        wm_conn = WMFMachineStatConnector()
        part_number = wm_conn.get_part_number()
        data = wm_conn.get_wmf_machine_info()
        data['part_number'] = str(wm_conn.part_number)
        with open('/root/wmf_1100_1500_5000_router/ip_address.json', 'w') as f:
            json.dump(data, f)
    if data and ip_address.startswith('10.8.'):
        data['ip_internal'] = ip_address
        requests.post('https://wmf24.ru/api/address', json=data)
    return data

def check_machine_status():
    initialize_logger('check_machine_status.log')
    db_driver = WMFSQLDriver()

    status = None
    try:
        ws = websocket.create_connection(settings.WS_URL, timeout=settings.WEBSOCKET_CONNECT_TIMEOUT)
        if ws.connected:
            ws.close()
            status = 1
    except Exception:
        status = 0

    logging.info(f'status is: {status}')
    last_id, end_time = None, None
    r = db_driver.get_error_last_stat_record('-1')
    #k = db_driver.get_error_last_stat_record('62')
    if r is not None:
        last_id, end_time = r
    else:
        end_time = time()
        last_id = 0
    render_errors_closing(last_id, end_time, status)

    #if k is not None:
     #   render_errors_closing(k, status)

    d_id = None
    d_date_start = None
    d_date_end = None
    d_status = None
    d = db_driver.get_last_downtime()
    if d:
        d_id, d_date_start, d_date_end, d_status = d
        if status == 1:
            logging.info(f'status == 1')
            logging.info(f'd_date_end: {d}')
            logging.info(f'd_date_end: {d_date_end}')
            if d_date_end == "" or d_date_end is None:
                logging.info(f'update')
                db_driver.update_downtime(d_id, datetime.datetime.now(), 1)
        elif status == 0:
            logging.info(f'status == 0')
            logging.info(f'd_date_end: {d_status}')
            logging.info(f'd_date_end: {d_date_end}')
            if d_status != "0":
                db_driver.create_downtime(datetime.datetime.now(), 0)
    logging.info(f'last_stat_record: {r}')
    logging.info(f'downtime_last_record: {d}')

    #db_driver.close()

def render_errors_closing(last_id, end_time, status):
    db_driver = WMFSQLDriver()
    if status == 0 and (end_time is None):
        logging.info(f'status is 0 and end_time is none, downtime is active')
    elif status == 0 and (end_time is not None):
        logging.info(f'status is 0 and end_time is {end_time}, calling create_error_record(-1)')
        db_driver.create_error_record('-1', 'Кофемашина недоступна')
    elif status == 1:
        logging.info(f'status is 1 and last_id is {last_id}, calling close_error_code_by_id({last_id})')
        if last_id != 0:
            db_driver.close_error_code_by_id(last_id)
        unclosed = db_driver.get_error_empty_record()
        for item in unclosed:  # 0 - id 1 - end_time 2 - code
            ws = websocket.create_connection(WS_URL)
            request = json.dumps({'function': 'isErrorActive', 'a_iErrorCode': item[2]})
            logging.info(f"COFFEE_MACHINE: Sending {request}")
            ws.send(request)
            received_data = ws.recv()
            if (WMFMachineStatConnector.normalize_json(received_data).get('returnvalue')) == 0:
                db_driver.close_error_code(item[2])



check_machine_status()
send_ip_address()
beverages_send_worker()
controller_data_statistics_sender()
