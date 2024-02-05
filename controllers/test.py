import websocket
import logging
import requests
import threading
import socket
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.core.utils import timedelta_int, get_beverages_send_time, initialize_logger
from controllers.api.beverages import methods
from controllers.wmf.models import WMFMachineStatConnector, WMFMachineErrorConnector

db_conn = WMFSQLDriver()

devices = db_conn.get_devices()
for device in devices:
    db_driver = WMFSQLDriver()
    WS_URL = f'ws://{device[2]}:25000/'
    wmf_conn = WMFMachineErrorConnector(device[1], device[2])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(device[2])
        if device[2] is not None:
            s.connect((device[2], 25000))
            s.send('{"function": "startPushDispensingFinished"}'.encode())
            s.send('{"function": "getMachineInfo"}'.encode())
            if s is not None:
                data = s.recv(1024)

    print(f"Received {data!r}")



