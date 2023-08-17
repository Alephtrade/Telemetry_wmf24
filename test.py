import json
import logging
import websocket
import ast
from datetime import datetime, timedelta
import sys
import requests

sys.path.append("../../")
from db.models import WMFSQLDriver
from core.utils import initialize_logger, get_beverages_send_time, get_part_number_local
from settings import prod as settings
from wmf.models import WMFMachineStatConnector

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def worker():
    print(db_conn.create_error_record(64, ""))
    return print(db_conn.create_error_record(64, ""))


print(worker())
