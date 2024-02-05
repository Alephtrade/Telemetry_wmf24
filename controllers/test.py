import websocket
import logging
import requests
import threading
import socket
import sys
import json
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.core.utils import timedelta_int, get_beverages_send_time, initialize_logger
from controllers.api.beverages import methods
from controllers.wmf.models import WMFMachineStatConnector, WMFMachineErrorConnector

db_conn = WMFSQLDriver()

devices = db_conn.get_devices()
for device in devices:
    db_driver = WMFSQLDriver()
    WS_URL = f'ws://10.8.0.6:25000/'
    wmf_conn = WMFMachineErrorConnector(device[1], device[2])
    ws = websocket.create_connection(WS_URL, timeout=5)
    status = db_conn.get_machine_block_status(device[1])[0][0]
    print(status)
    if status == 1:
        ws.send(json.dumps({"function": "shutdown"}))
    else:
        print("not 1")




