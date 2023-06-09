import requests
import websocket
import json
import logging
#rom core.utils import print_exception, get_env_mode
#from db.models import WMFSQLDriver

WS_IP = '192.168.8.101'
WS_PORT = 25000
WMF_BASE_URL = 'https://wmf24.ru'
WMF_DATA_URL = "https://wmf24.ru/api/test2"
WS_URL = f'ws://{WS_IP}:{WS_PORT}/'

def send_wmf_request(wmf_command):
    try:
        ws = websocket.create_connection(WS_URL, timeout=5)
    except Exception:
        ws = None
    request = wmf_command
    print(request)
    print("------------------------------")
    logging.info(f"WMFMachineStatConnector: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    logging.info(f"WMFMachineStatConnector: Received {received_data}")
    return (received_data)


s = input("API: ")
print(send_wmf_request(s))