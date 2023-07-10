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
initialize_logger('data_statistics_sender.log')

def worker():
    now_of_hour = str(datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60)))
    data_for_request = []
    wm_conn = WMFMachineStatConnector()
    try:
        with open('part_number.txt') as f:
            part_number = f.read()
    except Exception:
        return ''
    data_cleaning = methods.get_clean_info()
    data_main_stat = methods.get_main_data_stat()

    for item in data_cleaning:
        data_for_request.append(item)
    for key, item in data_main_stat.items():
        data_for_request.append({key: item})
    data_for_request.append({"code": part_number})
    data_for_request.append({"time_created": now_of_hour})
    return json.dumps(data_for_request)

    url = "https://wmf24.ru/api/reportdata"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(data_for_request))
    logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
    return response.text

print(worker())
