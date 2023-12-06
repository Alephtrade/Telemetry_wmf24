import requests
import json
import sys
import threading
import socket
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.db.models import WMFSQLDriver
db_conn = WMFSQLDriver()


def asker():
    url = "https://wmf24.ru/api/vpn_server_send_interval"
    data_for_request = {}
    h_name = socket.gethostname()
    server_ip = socket.gethostbyname(h_name)
    data_for_request["ip"] = server_ip
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=data_for_request)
    json_res = response.json()
    db_conn.update_exchange_time(json_res['minutes'])


asker()