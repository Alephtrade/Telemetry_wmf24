import sys
import websocket
import logging
import requests
import json
import time

import ast
import socket
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from datetime import timedelta, datetime, date
from controllers.api.beverages import methods
from timezonefinder import TimezoneFinder
from datetime import datetime, timezone
import pytz
sys.path.append("../../")
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.wmf.models import WMFMachineStatConnector, WMFMachineErrorConnector
from controllers.core.utils import initialize_logger, print_exception, get_beverages_send_time, timedelta_int
#
#
#WMF_URL = settings.WMF_DATA_URL
#WS_URL = settings.WS_URL
#DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()
def get_service_statistics(device):
    initialize_logger('getServiceStatistics.log')
    date_today = date.today()
    logging.info(f"COFFEE_MACHINE: today date in service_stat {date_today}")

    # print(date_today)
    try:
        WS_IP = f'ws://{device[2]}:25000/'
        ws = websocket.create_connection(WS_IP, timeout=5)
    except Exception:
        ws = None
        logging.info(f"error {ws}")
        return False
    actual = db_conn.get_last_service_statistics(device[1], date_today)
    logging.info(f"COFFEE_MACHINE: last service_stat record {actual}")
    # print(actual)
    if actual is None:
        #print("create")
        record = db_conn.create_service_record(device[1], date_today)
        logging.info(f"COFFEE_MACHINE: created record service_stat {record}")
        actual = db_conn.get_last_service_statistics(device[1], date_today)
    else:
        if actual[2] == "0":
    # print("form")
            request = json.dumps({'function': 'getServiceStatistics'})
            logging.info(f"COFFEE_MACHINE: Sending {request}")
            ws.send(request)
            received_data = ws.recv()
            logging.info(f"servicestatistics: Received {received_data}")
            logging.info(f"COFFEE_MACHINE: Received {device[1]}")
            text_file = open("response.txt", "a")
            text_file.write(received_data)
            ts = time.time()
            int_ts = int(ts)
            received_data = received_data.replace(']', '', 1)
            received_data = received_data + ', {"device" : "' + str(device[1]) + '"}, {"timestamp_create" : ' + str(
                int_ts) + '}]'
            print(received_data)
            url = "https://backend.wmf24.ru/api/servicestatistics"
            headers = {
                'Content-Type': 'application/json',
                'Serverkey': db_conn.get_encrpt_key()[0]
            }
            print(received_data)
            response = requests.request("POST", url, headers=headers, data=received_data)
            logging.info(f"servicestatistics: GET response: {response.text}")
            db_conn.save_status_service_statistics(actual[0], "date_fact_send",
                                                   str(datetime.fromtimestamp(int((datetime.now()).timestamp()))))
            db_conn.save_status_service_statistics(actual[0], "is_sent", "1")
            ws.close()
            print(response.text)
            return response


devices = db_conn.get_devices()
for device in devices:
    print(get_service_statistics(device))
