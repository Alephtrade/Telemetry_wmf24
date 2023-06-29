import json
import logging
import websocket
import ast
from datetime import datetime, timedelta
import sys
sys.path.append("../../")
from db.models import WMFSQLDriver
from core.utils import initialize_logger, get_beverages_send_time
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def Take_Create_Beverage_Statistics():
    #initialize_logger('response.txt')
    ws = websocket.create_connection(WS_URL)
    request = json.dumps({'function': 'getBeverageStatistics'})
    #logging.info(f"COFFEE_MACHINE: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    #logging.info(f"COFFEE_MACHINE: Received {received_data}")
    try:
        with open('part_number.txt') as f:
            part_number = f.read()
    except Exception:
        return ''
    #logging.info(f"COFFEE_MACHINE: Received {part_number}")
    #text_file = open("response.txt", "a")
    #text_file.write(received_data)
    received_data = received_data.replace(']', '', 1)
    received_data = received_data + ', {"device_code" : ' + str(part_number) + '}]'
    logging.info(f"beveragestatistics: Received {received_data}")
    received = ast.literal_eval(received_data)
    summ = 0
    device_code = ""
    recipes = []
    date_to_send = get_beverages_send_time()
    print(date_to_send)
    date_formed = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
    for item in received:
        print(item)
        for k, item2 in item.items():
            print(item2)
            if (k.startswith("device_code")):
                device_code = item2
            if (k.startswith("TotalCountRcp")):
                summ += item2
                recipes.append(item)

    create_record = db_conn.create_beverages_log(device_code, summ, date_to_send, 0, date_formed, json.dumps(recipes))
    #url = "https://wmf24.ru/api/beveragestatistics"
    #headers = {
    #    'Content-Type': 'application/json'
    #}
    #response = requests.request("POST", url, headers=headers, data=received_data)
    #logging.info(f"beveragestatistics: GET response: {response.text}")
    ws.close()
    return True
