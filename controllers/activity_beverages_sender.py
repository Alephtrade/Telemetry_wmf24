import websocket
import logging
import requests
import json
import ast
import socket
from datetime import timedelta, datetime, time
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.core.utils import timedelta_int, get_beverages_send_time, initialize_logger
from controllers.api.beverages import methods
from controllers.wmf.models import WMFMachineStatConnector


def beverages_send_worker(aleph_id, ip):
    initialize_logger('beverages_send_worker.py.log')
    k = []
    time_to_send = None
    receive_data = db_conn.get_not_sended_beverages_log(aleph_id)
    if(receive_data == []):
        logging.info(f'NO DATA')
    else:
        for item in receive_data:
            logging.info(f'loop')
            time_to_send = item[2]
            k.append({"device": item[0]})
            k.append({"summ": item[1]})
            k.append({"time_to_send": item[2]})
            k.append({"time_fact_send": item[3]})
            k.append({"date_formed": item[4]})
            data_info = ast.literal_eval(str(item[5]))
            record_id = item[6]
            for item_info in data_info:
                k.append(item_info)
            next_time = datetime.strptime(time_to_send, '%Y-%m-%d %H:%M:%S')
            if datetime.fromtimestamp(int(datetime.now().timestamp())) > next_time:
                print(json.dumps(k))
                methods.Send_Statistics(json.dumps(k), record_id)
                logging.info(f'Send_Statistics db id - {record_id}')
            else:
                logging.info(f'wrong time to_sent - {next_time}')
    return True


def controller_data_statistics_sender(aleph_id, ip):
    initialize_logger('controller_data_statistics_sender.py.log')
    now_of_hour = str(datetime.fromtimestamp(int(datetime.now().timestamp())))
    data_for_request = []
    data_main_stat = db_conn.get_data_statistics_to_send(aleph_id)
    if data_main_stat is not None:
        print(data_main_stat)
        for item in data_main_stat:
            print(item)
            print(datetime.strptime(item[6], '%Y-%m-%d %H:%M:%S'))
            print(datetime.fromtimestamp(int(datetime.now().timestamp())))
            if datetime.strptime(item[6], '%Y-%m-%d %H:%M:%S') < datetime.fromtimestamp(int(datetime.now().timestamp())):
                print("YES")
                data_for_request.append({"time_worked": item[0]})
                data_for_request.append({"wmf_error_count": item[1]})
                data_for_request.append({"wmf_error_time": item[2]})
                data_for_request.append({"stoppage_count": item[3]})
                data_for_request.append({"stoppage_time": item[4]})
                data_for_request.append({"date_formed": item[5]})
                data_for_request.append({"time_to_send": item[6]})
                data_for_request.append({"time_fact_send": item[7]})
                data_for_request.append({"is_sent": item[8]})
                data_for_request.append({"device": aleph_id})
                url = "https://backend.wmf24.ru/api/machineactivity"
                headers = {
                    'Content-Type': 'application/json',
                    'Serverkey': db_conn.get_encrpt_key()[0]
                }
                print(json.dumps(data_for_request))
                response = requests.request("POST", url, headers=headers, data=json.dumps(data_for_request))
                print(response.text)
                logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
                print(item[9])
                db_conn.save_status_data_statistics(item[9], "is_sent", "1")
                db_conn.save_status_data_statistics(item[9], "time_fact_send", now_of_hour)
                logging.info(f'{datetime.now()} {response.text}')
            logging.info(f'Done')
    logging.info(f'nothing to send')
    return True

def send_ip_address(aleph_id, ip):
    data = {}
    if data["ip"] is not None:
        data['aleph_id'] = aleph_id
        data["ip"] = ip
        url = "https://backend.wmf24.ru/api/machine_ip_address"
        headers = {
            'Content-Type': 'application/json',
            'Serverkey': db_conn.get_encrpt_key()[0]
        }
        requests.request("POST", url, headers=headers, json=data)
        print(ip)
        return data

def check_machine_status(aleph_id, ip):
    initialize_logger('check_machine_status.log')
    db_driver = WMFSQLDriver()
    WS_URL = f'ws://{ip}:25000/'

    status = None
    try:
        ws = websocket.create_connection(WS_URL, timeout=settings.WEBSOCKET_CONNECT_TIMEOUT)
        if ws.connected:
            ws.close()
            status = 1
    except Exception:
        status = 0
    logging.info(f'status is: {status}')
    last_id, end_time = None, None
    r = db_driver.get_error_last_stat_record('-1', aleph_id)
    if r is not None:
        last_id, end_time = r
    else:
        end_time = time()
        last_id = 0
    render_errors_closing(aleph_id, ip, last_id, end_time, status)
    db_driver.update_device_ping_time(aleph_id, status, datetime.fromtimestamp(int(datetime.now().timestamp())))
    return status

    #db_driver.close()

def render_errors_closing(aleph_id, ip, last_id, end_time, status):
    WS_URL = f'ws://{ip}:25000/'
    db_driver = WMFSQLDriver()
    if status == 0 and (end_time is None):
        logging.info(f'status is 0 and end_time is none, downtime is active')
    elif status == 0 and (end_time is not None):
        logging.info(f'status is 0 and end_time is {end_time}, calling create_error_record(-1)')
        print(status)
        print(end_time)
        db_driver.create_error_record(aleph_id, '-1')
    elif status == 1:
        logging.info(f'status is 1 and last_id is {last_id}, calling close_error_code_by_id({last_id})')
        if last_id != 0:
            db_driver.close_error_code_by_id(aleph_id, last_id)
        unclosed = db_driver.get_error_empty_record(aleph_id)
        for item in unclosed:  # 0 - id 1 - end_time 2 - code
            ws = websocket.create_connection(WS_URL)
            request = json.dumps({'function': 'isErrorActive', 'a_iErrorCode': item[2]})
            logging.info(f"COFFEE_MACHINE: Sending {request}")
            ws.send(request)
            received_data = ws.recv()
            if (WMFMachineStatConnector.normalize_json(received_data).get('returnvalue')) == 0:
                db_driver.close_error_code(aleph_id, item[2])


db_conn = WMFSQLDriver()
devices = db_conn.get_devices()
print(devices)

result = []
for device in devices:
    if device[2] is not None:
        send_ip_address(device[1], device[2])
        print(check_machine_status(device[1], device[2]))
        beverages_send_worker(device[1], device[2])
        controller_data_statistics_sender(device[1], device[2])
