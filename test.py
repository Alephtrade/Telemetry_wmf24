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
    data = WMFMachineStatConnector.send_wmf_request('getMachineInfo')
    print(data)
    print(1)
    request = json.dumps({'function': 'getMachineInfo'})
    logging.info(f"WMFMachineStatConnector: Sending {request}")
    WMFMachineStatConnector.ws.send(request)
    received_data = WMFMachineStatConnector.ws.recv()
    logging.info(f"WMFMachineStatConnector: Received {received_data}")
    print(WMFMachineStatConnector.normalize_json(received_data))
    part_number = data.get('PartNumber')
    with open('/root/wmf_1100_1500_5000_router/part_number.txt', 'w') as f:
        f.write(str(part_number))
    return part_number

print(worker())
