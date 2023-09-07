import sys
import websocket
import logging
import requests
import json
import ast
import socket
from datetime import timedelta, datetime
from api.beverages import methods


sys.path.append("../../")
from db.models import WMFSQLDriver
from settings import prod as settings
from wmf.models import WMFMachineStatConnector, WMFMachineErrorConnector
from core.utils import initialize_logger, get_beverages_send_time


WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_driver = WMFSQLDriver()
wmf_conn = WMFMachineErrorConnector()
wmf2_conn = WMFMachineStatConnector()

def worker():
    status = None
    try:
        ws = websocket.create_connection(settings.WS_URL, timeout=settings.WEBSOCKET_CONNECT_TIMEOUT)
        if ws.connected:
            ws.close()
            status = 1
    except Exception:
        status = 0
    r = db_driver.get_error_last_stat_record('62')
    if r is not None:
        last_id, end_time = r
    if status == 0 and (end_time is None):
        logging.info(f'status is 0 and end_time is none, downtime is active')
    elif status == 0 and (end_time is not None):
        logging.info(f'status is 0 and end_time is {end_time}, calling create_error_record(-1)')
        db_driver.create_error_record('-1', 'Кофемашина недоступна')
    elif status == 1:
        logging.info(f'status is 1 and last_id is {last_id}, calling close_error_code_by_id({last_id})')
        db_driver.close_error_code_by_id(last_id)
        unclosed = db_driver.get_error_empty_record()
        for item in unclosed: #0 - id 1 - end_time 2-code
            ws = websocket.create_connection(WS_URL)
            request = json.dumps({'function': 'isErrorActive', 'a_iErrorCode': item[2]})
            logging.info(f"COFFEE_MACHINE: Sending {request}")
            ws.send(request)
            received_data = ws.recv()
            if (WMFMachineStatConnector.normalize_json(received_data).get('returnvalue')) == 0:
                db_driver.close_error_code_by_id(item[2])

print(worker())
