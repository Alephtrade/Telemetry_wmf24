import requests
import json
import logging
import websocket
from core.utils import initialize_logger, get_part_number_local
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
def getServiceStatistics():
    initialize_logger('response.txt')
    ws = websocket.create_connection(WS_URL)
    request = json.dumps({'function': 'getServiceStatistics'})
    logging.info(f"COFFEE_MACHINE: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    logging.info(f"COFFEE_MACHINE: Received {received_data}")
    part_number = get_part_number_local()
    logging.info(f"COFFEE_MACHINE: Received {part_number}")
    text_file = open("response.txt", "a")
    text_file.write(received_data)
    received_data = received_data.replace(']', '', 1)
    received_data = received_data + ', {"device_id" : ' + str(part_number) + '}]'
    # received_data.append({"device_id": part_number})
    # r = requests.post('https://wmf24.ru/api/servicestatistics', json=received_data)
    url = "https://wmf24.ru/api/servicestatistics"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=received_data)
    logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
    ws.close()
    return True

def getBeverageStatistics():
    initialize_logger('response.txt')
    ws = websocket.create_connection(WS_URL)
    request = json.dumps({'function': 'getBeverageStatistics'})
    logging.info(f"COFFEE_MACHINE: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    logging.info(f"COFFEE_MACHINE: Received {received_data}")
    part_number = get_part_number_local()
    logging.info(f"COFFEE_MACHINE: Received {part_number}")
    text_file = open("response.txt", "a")
    text_file.write(received_data)
    received_data = received_data.replace(']', '', 1)
    received_data = received_data + ', {"device_id" : ' + str(part_number) + '}]'
    # received_data.append({"device_id": part_number})
    # r = requests.post('https://wmf24.ru/api/servicestatistics', json=received_data)
    url = "https://wmf24.ru/api/beveragestatistics"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=received_data)
    logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
    ws.close()
    return True

