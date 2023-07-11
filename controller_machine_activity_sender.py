import json
import requests
import logging
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
    now_of_hour = str(datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())))
    data_for_request = []
    wm_conn = WMFMachineStatConnector()
    try:
        with open('part_number.txt') as f:
            part_number = f.read()
    except Exception:
        return ''
    data_main_stat = db_conn.get_machine_activity_to_send()

    for item in data_main_stat:
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
        return response.text
    return "DONE"

print(worker())
