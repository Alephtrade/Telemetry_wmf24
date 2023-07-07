import json
import requests
import logging
from api.datastat import methods
from datetime import timedelta, datetime
from db.models import WMFSQLDriver
from core.utils import timedelta_str, get_curr_time, initialize_logger
from wmf.models import WMFMachineStatConnector
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()
initialize_logger('test.log')

def worker():

    wm_conn = WMFMachineStatConnector()
    if not wm_conn.ws:
        return False

    data_cleaning = methods.get_clean_info()
    data_main_stat = methods.get_main_data_stat()

    return data_main_stat

    data['code'] = wm_conn.part_number

    url = "https://wmf24.ru/api/reportdata"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
    return response.text

print(worker())

