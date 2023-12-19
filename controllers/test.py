import sys
import websocket
import logging
import requests
import json
import time
from collections import deque
import ast
import socket
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings

db_conn = WMFSQLDriver()

devices = db_conn.get_devices()
for device in devices:
    WS_URL = f'ws://{devices[2]}:{settings.WS_PORT}/'
    ws = websocket.create_connection(WS_URL, timeout=5)
    request = json.dumps({"function": "getRecipeComposition", "RecipeNumber": 27})
    print()
    print(request)
    print("------------------------------")
    logging.info(f"WMFMachineStatConnector: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    logging.info(f"WMFMachineStatConnector: Received {received_data}")
    received_data2 = deque(json.loads(received_data))
    formatted = {}
    for var in list(received_data2):
        for i in var:
            formatted[i] = var[i]
    formatted["ip"] = ip
    return formatted
