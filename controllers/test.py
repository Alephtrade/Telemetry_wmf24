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
def controller_data_statistics_sender(aleph_id):
    initialize_logger('controller_data_statistics_sender.py.log')
    now_of_hour = str(datetime.fromtimestamp(int(datetime.now().timestamp())))
    data_for_request = []
    data_main_stat = db_conn.get_data_statistics_to_send(aleph_id)
    if data_main_stat is not None:
        print(data_main_stat)
        for item in data_main_stat:
            print(item)
            if datetime.strptime(item[6], '%Y-%m-%d %H:%M:%S') < datetime.fromtimestamp(int(datetime.now().timestamp())):
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
                logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
                print(response.text)
                print(item[9])
                db_conn.save_status_data_statistics(item[9], "is_sent", "1")
                db_conn.save_status_data_statistics(item[9], "time_fact_send", now_of_hour)
                logging.info(f'{datetime.now()} {response.text}')
            logging.info(f'Done')
    logging.info(f'nothing to send')
    return True


devices = db_conn.get_devices()
for device in devices:
    print(controller_data_statistics_sender(device[0]))
