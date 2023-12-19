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
    columns = {
        "water": {"count": 0, "weight": 0},
        "coffee": {"count": 0, "weight": 0},
        "milk": {"count": 0, "weight": 0},
        "powder": {"count": 0, "weight": 0},
        "foam": {"count": 0, "weight": 0},
    }
    WS_URL = f'ws://{device[2]}:{settings.WS_PORT}/'
    ws = websocket.create_connection(WS_URL, timeout=5)
    request = json.dumps({"function": "getRecipeComposition", "RecipeNumber": 88})
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
        print(formatted["Parts"])
        if vat["Type"] == "coffee":
            columns["coffee"]["weight"] = columns["coffee"]["weight"] + vat['QtyPowder']
            columns["coffee"]["count"] = columns["coffee"]["count"] + 1
        if vat["Type"] == "coldmilk" or vat["Type"] == "milk":
            columns["milk"]["weight"] = columns["milk"]["weight"] + vat['QtyMilk']
            columns["milk"]["count"] = columns["milk"]["count"] + 1
        if vat["Type"] == "milkfoam" or vat["Type"] == "coldfoam":
            columns["foam"]["weight"] = columns["foam"]["weight"] + vat['QtyFoam']
            columns["foam"]["count"] = columns["foam"]["count"] + 1
        if vat["Type"] == "hotwater" or vat["Type"] == "water":
            columns["water"]["weight"] = columns["water"]["weight"] + vat['QtyWater']
            columns["water"]["count"] = columns["water"]["count"] + 1
    print(columns)

    #print(formatted)
