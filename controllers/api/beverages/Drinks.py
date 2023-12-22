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
from controllers.core.utils import initialize_logger, print_exception
from controllers.wmf.models import WMFMachineErrorConnector
from controllers.settings import prod as settings
from controllers.db.models import WMFSQLDriver

db_conn = WMFSQLDriver()
devices = db_conn.get_devices()

def updateDrinks():
    for device in devices:
        try:
            ws = websocket.create_connection(f'ws://{device[2]}:25000/', timeout=5)
            status = 1
        except Exception:
            return False
        request = json.dumps({"function": "getDrinkList"})
        print(request)
        ws.send(request)
        received_data = ws.recv()
        received_data2 = deque(json.loads(received_data))
        formatted = {}
        for var in list(received_data2):
            for i in var:
                formatted[i] = var[i]
        for drink in formatted["DrinkList"]:
            print(drink["name"])


updateDrinks()