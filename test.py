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
from core.utils import initialize_logger, get_beverages_send_time


WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()
wmf_conn = WMFMachineErrorConnector()
wmf2_conn = WMFMachineStatConnector()

def worker():
    return [wmf2_conn.get_error_active_count(), wmf2_conn.get_error_active()]

print(worker())
