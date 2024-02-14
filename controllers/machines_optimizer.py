import sys
import websocket
import requests
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from datetime import datetime, timezone
from controllers.db.models import WMFSQLDriver

db_conn = WMFSQLDriver()


def status_send_anyway(status_machine, device_aleph_id):
    data = {'aleph_id': device_aleph_id, "status": status_machine}
    url = "https://backend.wmf24.ru/api/km_status"
    headers = {
        'Content-Type': 'application/json',
        'Serverkey': db_conn.get_encrpt_key()[0]
    }
    response = requests.request("POST", url, headers=headers, json=data)


devices = db_conn.get_devices()
for device in devices:
    WS_URL = f'ws://{device[2]}:25000/'
    try:
        ws = websocket.create_connection(WS_URL, timeout=5)
        status = 1
    except Exception:
        ws = False
        status = 0
    last_record = db_conn.get_error_last_stat_record("-1", device[1])
    if last_record[1] is None:
        db_conn.create_error_record(device[1], '-1')
    status_send_anyway(status, device[1])
    if ws == False:
        db_conn.reset_ips(device[1])
    if int(datetime.strptime(device[4], '%Y-%m-%d %H:%M:%S').timestamp()) + 2419200 < int(
            datetime.now().timestamp()):
        db_conn.delete_device(device[0])
    if int(datetime.strptime(device[4], '%Y-%m-%d %H:%M:%S').timestamp()) + 43200 < int(datetime.now().timestamp()):
        db_conn.reset_ips(device[0])

