import requests
import json
import logging
import websocket
from db.models import WMFSQLDriver
from core.utils import initialize_logger
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def getServiceStatistics():
    initialize_logger('response.txt')
    ws = websocket.create_connection(WS_URL)
    request = json.dumps({'function': 'getServiceStatistics'})
    logging.info(f"COFFEE_MACHINE: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    logging.info(f"servicestatistics: Received {received_data}")
    try:
        with open('part_number.txt') as f:
            part_number = f.read()
    except Exception:
        return ''
    logging.info(f"COFFEE_MACHINE: Received {part_number}")
    text_file = open("response.txt", "a")
    text_file.write(received_data)
    received_data = received_data.replace(']', '', 1)
    received_data = received_data + ', {"device_code" : ' + str(part_number) + '}]'

    url = "https://wmf24.ru/api/servicestatistics"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=received_data)
    logging.info(f"servicestatistics: GET response: {response.text}")
    ws.close()
    return True


getServiceStatistics()

