import logging
import requests
from db.models import WMFSQLDriver
from settings import prod as settings
from core.utils import initialize_logger

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def Send_Statistics(data):
    initialize_logger('Send_Statistics.txt')
    logging.info(f"beveragestatistics: GET request: {data}")
    url = "https://wmf24.ru/api/beveragestatistics"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=data)
    logging.info(f"beveragestatistics: GET response: {response.text}")
    return True