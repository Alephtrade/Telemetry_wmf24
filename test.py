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
from core.utils import initialize_logger, print_exception, get_env_mode, get_part_number_local


WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_driver = WMFSQLDriver()
wmf_conn = WMFMachineErrorConnector()
wmf2_conn = WMFMachineStatConnector()

def worker():
    try_to_get_part_number = get_part_number_local()
    if try_to_get_part_number is None:
        try_to_get_part_number = get_part_number()
    print(try_to_get_part_number)

def get_part_number():
    try:
         ws = websocket.create_connection(WS_URL)
         request = json.dumps({'function': 'getMachineInfo'})
         logging.info(f"COFFEE_MACHINE: Sending {request}")
         ws.send(request)
         received_data = ws.recv()
         print(received_data)
         ws.close()
         return WMFMachineStatConnector.normalize_json(received_data).get('PartNumber')
    except Exception as ex:
        logging.info(f"COFFEE_MACHINE: Get machine info error, HOST {WS_URL} - {ex}")
        print(ex)
        return None

print(worker())
