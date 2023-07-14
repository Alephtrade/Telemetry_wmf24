import websocket
import logging
import requests
import json
import ast
from datetime import timedelta, datetime
from db.models import WMFSQLDriver
from settings import prod as settings
from core.utils import timedelta_int, get_beverages_send_time, initialize_logger
from api.beverages import methods


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
            data_info = ast.literal_eval((item[5]))
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


def controller_machine_activity_sender():
    initialize_logger('controller_machine_activity_sender.py.log')
    now_of_hour = str(datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())))
    data_for_request = []
    try:
        with open('part_number.txt') as f:
            part_number = f.read()
    except Exception:
        logging.info(f'{part_number} is none')
    data_main_stat = db_conn.get_machine_activity_to_send()
    if data_main_stat is not None:
        for item in data_main_stat:
            if datetime.strptime(item[6], '%Y-%m-%d %H:%M:%S') < datetime.now():
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
                db_conn.save_status_machine_activity(item[9], "is_sent", "1")
                db_conn.save_status_machine_activity(item[9], "time_fact_send", now_of_hour)
                logging.info(f'{datetime.now()} {response.text}')
            logging.info(f'Done')
    logging.info(f'nothing to send')
    return True


beverages_send_worker()
controller_machine_activity_sender()
