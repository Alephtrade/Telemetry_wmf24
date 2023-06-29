import json
import logging
import websocket
import ast
from datetime import datetime
from db.models import WMFSQLDriver
from core.utils import initialize_logger, get_beverages_send_time
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def Send_Statistics():
    return True