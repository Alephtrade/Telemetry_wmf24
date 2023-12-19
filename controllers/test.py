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
columns = {
    "water": {"count": 0, "weight": 0},
    "coffe": {"count": 0, "weight": 0},
    "milk": {"count": 0, "weight": 0},
    "powder": {"count": 0, "weight": 0},
    "foam": {"count": 0, "weight": 0},
}
devices = db_conn.get_devices()
for device in devices:
    WS_URL = f'ws://{device[2]}:{settings.WS_PORT}/'
    ws = websocket.create_connection(WS_URL, timeout=5)
    request = json.dumps({"function": "getRecipeComposition", "RecipeNumber": 27})
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
    for vat in formatted["Parts"]:
        print(device[2])
        print(vat["Type"])
        print(formatted)
        if vat["Type"] == "coldmilk" or vat["Type"] == "milk":
            print("milk")
        if vat["Type"] == "milkfoam " or vat["Type"] == "coldfoam":
            print("foam")
        if vat["Type"] == "hotwater " or vat["Type"] == "water":
            print("water")
        if vat["Type"] == "coldmilk" or vat["Type"] == "milk":
            print("milk")
    #print(formatted)
