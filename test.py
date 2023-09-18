import sys
import websocket
import logging
import requests
import json
import ast
import socket
from datetime import timedelta, datetime
from api.beverages import methods


sys.path.append("../../")
from db.models import WMFSQLDriver
from settings import prod as settings
from wmf.models import WMFMachineStatConnector, WMFMachineErrorConnector
from core.utils import initialize_logger, print_exception, get_env_mode, get_part_number_local


WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_driver = WMFSQLDriver()
wmf_conn = WMFMachineErrorConnector()
wmf2_conn = WMFMachineStatConnector()

def worker():
    time_now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
    print(db_driver.get_error_records(time_now - timedelta(hours=1), time_now))


print(worker())
