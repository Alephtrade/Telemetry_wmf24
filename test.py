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
    last_error_id = db_conn.get_error_last_record()
    print(last_error_id)
    if (last_error_id[0] != "62" and last_error_id[0] != "-1" and last_error_id[1] is not None):
        return True


print(worker())
