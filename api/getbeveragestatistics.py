import json
import logging
import websocket
from core.utils import initialize_logger
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
WMF_URL = settings.WMF_DATA_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
initialize_logger('response.txt')
ws = websocket.create_connection(WS_URL)
request = json.dumps({'function': 'getBeverageStatistics'})
logging.info(f"COFFEE_MACHINE: Sending {request}")
ws.send(request)
received_data = ws.recv()
logging.info(f"COFFEE_MACHINE: Received {received_data}")
text_file = open("response.txt", "w")
text_file.write(received_data)
ws.close()

