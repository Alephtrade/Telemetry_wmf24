import json
import logging
import websocket
import ast
from datetime import datetime, timedelta
import sys
import requests
sys.path.append("../../")
from db.models import WMFSQLDriver
from core.utils import initialize_logger, get_beverages_send_time
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def Take_Create_Beverage_Statistics():
    ws = websocket.create_connection(WS_URL)
    request = json.dumps({'function': 'getBeverageStatistics'})
    ws.send(request)
    received_data = ws.recv()
    try:
        with open('part_number.txt') as f:
            part_number = f.read()
    except Exception:
        return ''
    received_data = received_data.replace(']', '', 1)
    received_data = received_data + ', {"device_code" : ' + str(part_number) + '}]'
    logging.info(f"beveragestatistics: Received {received_data}")
    received = ast.literal_eval(received_data)
    summ = 0
    device_code = ""
    recipes = []
    date_to_send = get_beverages_send_time()
    #print(date_to_send)
    date_formed = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
    for item in received:
        #print(item)
        for k, item2 in item.items():
            #print(item2)
            if (k.startswith("device_code")):
                device_code = item2
            if (k.startswith("TotalCountRcp")):
                summ += item2
                recipes.append(item)

    create_record = db_conn.create_beverages_log(device_code, summ, date_to_send, 0, date_formed, json.dumps(recipes))
    ws.close()
    return create_record

def Send_Statistics(data):
    initialize_logger('Send_Statistics.txt')
    logging.info(f"beveragestatistics: GET request: {data}")
    url = "https://wmf24.ru/api/beveragestatistics"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=data)
    return response.text
    return True
