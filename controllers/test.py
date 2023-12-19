import sys
import websocket
import logging
import requests
import json
import time

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
    ws = websocket.create_connection(WS_URL, timeout=settings.WEBSOCKET_CONNECT_TIMEOUT)
    print(ws.send(json.dumps({"function": "getRecipeComposition", "RecipeNumber": 27})).recv())
