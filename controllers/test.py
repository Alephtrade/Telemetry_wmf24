import websocket
import logging
import requests
import json
import ast
import socket
from datetime import timedelta, datetime, time
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.core.utils import timedelta_int, get_beverages_send_time, initialize_logger
from controllers.api.beverages import methods
from controllers.wmf.models import WMFMachineStatConnector
db_conn = WMFSQLDriver()

devices = db_conn.get_devices()
for device in devices:
    db_driver = WMFSQLDriver()
    WS_URL = f'ws://{device[2]}:25000/'

    status = None
    try:
        ws = websocket.create_connection(WS_URL, timeout=settings.WEBSOCKET_CONNECT_TIMEOUT)
        if ws.connected:
            ws.close()
            status = 1
    except Exception:
        status = 0
    #logging.info(f'status is: {status}')
    print(status)
    #print(formatted)
