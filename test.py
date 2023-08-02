import json
import logging
import websocket
import ast
from datetime import datetime, timedelta
import sys
import requests

sys.path.append("../../")
from db.models import WMFSQLDriver
from core.utils import initialize_logger, get_beverages_send_time, get_part_number_local
from settings import prod as settings
from wmf.models import WMFMachineStatConnector

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def worker():
    try_to_get_part_number = get_part_number_local()
    unset_errors = db_conn.get_unsent_records()
    content = None
    if unset_errors:
        for record in unset_errors:
            request = f'{WMF_URL}?code={try_to_get_part_number}&{DEFAULT_WMF_PARAMS}&error_id={record[1]}&date_start={record[2]}&date_end={record[3]}&duration={record[5]}&status=1'
            response = requests.post(request)
            content = response.content.decode('utf-8')
            db_conn.set_report_sent(record[0])
    print(content)
    return content


print(worker())

