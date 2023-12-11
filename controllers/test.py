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
def sender_report(device):
    data = db_conn.get_clean_or_rins_to_send(device[1])
    date_formatted = []
    if data is not None:
        for item in data:
            date_formatted.append({"cleaning_alias": item[1]})
            date_formatted.append({"type_last_cleaning_datetime": item[2]})
            date_formatted.append({"type_cleaning_duration": item[3]})
            date_formatted.append({"date_formed": item[4]})
            date_formatted.append({"device": device[1]})
            url = "https://backend.wmf24.ru/api/datastat"
            headers = {
                'Content-Type': 'application/json',
                'Serverkey': db_conn.get_encrpt_key()[0]
            }
            print(json.dumps(date_formatted))
            response = requests.request("POST", url, headers=headers, data=json.dumps(date_formatted))
            print(response.text)
            logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
            db_conn.save_status_clean_or_rins(item[0], "is_sent", "2")
    else:
        logging.info(f'{data} is none')


devices = db_conn.get_devices()
for device in devices:
    print(sender_report(device))
