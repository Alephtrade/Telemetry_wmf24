import json
import logging
import websocket
import ast
from datetime import datetime, timedelta
import sys
import requests
sys.path.append("../../")
from controllers.db.models import WMFSQLDriver
from controllers.core.utils import initialize_logger, get_beverages_send_time
from controllers.settings import prod as settings
from controllers.wmf.models import WMFMachineStatConnector

WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()


def Take_Create_Beverage_Statistics(last_send, device):
    initialize_logger('beveragestatistics.log')
    wm_conn = WMFMachineStatConnector(device[1], device[2])
    fake_data = False
    summ = 0
    device_code = ""
    recipes = []
    date_to_send = get_beverages_send_time(last_send)
    next_time = datetime.strptime(str(date_to_send), '%Y-%m-%d %H:%M:%S')
    #date_to_send = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    date_formed = datetime.fromtimestamp(int(datetime.now().timestamp()))
    try:
        WS_IP = f'ws://{device[2]}:25000/'
        ws = websocket.create_connection(WS_IP, timeout=5)
    except Exception:
        ws = None
        fake_data = True
        logging.info(f"error {wm_conn.ws}")
    if not wm_conn.ws:
        logging.info(f"error {wm_conn.ws}")
        fake_data = True
    else:
        request = json.dumps({'function': 'getBeverageStatistics'})
        ws.send(request)
        received_data = ws.recv()
        logging.info(f"{received_data}")
        if received_data is not None or received_data != []:
            received_data = received_data.replace(']', '', 1)
            received_data = received_data + ', {"device" : ' + '"' + device[1] + '"' + '}]'
            logging.info(f"beveragestatistics: Received {received_data}")
            received = ast.literal_eval(received_data)
            for item in received:
                for k, item2 in item.items():
                    if (k.startswith("device_code")):
                        device_code = item2
                    if (k.startswith("TotalCountRcp")):
                        recipes.append(item)
                        summ += item2
            #summ = wm_conn.get_beverages_count()
            ws.close()
    if fake_data:
        create_record = None
        #last_record = db_conn.get_last_beverages_log()
        #if last_record is None:
        #    create_record = db_conn.create_beverages_log(part_number, "0", "1970-01-01 00:00:00", "1970-01-01 00:00:00", "[{'TotalCountRcp': 0}]")
        #else:
           # create_record = db_conn.create_beverages_log(str(last_record[0]), str(last_record[1]), str(last_record[2]), str(date_formed), str(last_record[5]))
    else:
        if recipes == []:
            create_record = None
            #Take_Create_Beverage_Statistics(last_send)
        else:
            create_record = db_conn.create_beverages_log(device[1], str(summ), str(date_to_send), str(date_formed), json.dumps(recipes))
            logging.info(f"result {create_record}")
    return create_record


def Send_Statistics(data_info, id_record):
    initialize_logger('beverages_send_worker.py.log')
    logging.info(f"beveragestatistics: GET request: {data_info}")
    url = "https://backend.wmf24.ru/api/beveragestatistics"
    headers = {
        'Content-Type': 'application/json',
        'Serverkey': db_conn.get_encrpt_key()
    }
    response = requests.request("POST", url, headers=headers, data=data_info)
    json_res = response.json()
    now = datetime.fromtimestamp(int((datetime.now()).timestamp()))
    if(json_res["id"]):
        update_record = db_conn.update_beverages_log(id_record, now)
        logging.info(f"update {update_record}")
    else:
        logging.info(f"error unknown id record")
    return response.json()
