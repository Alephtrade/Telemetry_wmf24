import sys
import websocket
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from datetime import datetime, timezone
from controllers.db.models import WMFSQLDriver

db_conn = WMFSQLDriver()

devices = db_conn.get_devices()
for device in devices:
    WS_URL = f'ws://{device[2]}:25000/'
    try:
        ws = websocket.create_connection(WS_URL, timeout=5)
    except Exception:
        ws = False
    if ws == False:
        db_conn.reset_ips(device[1])
    if int(datetime.strptime(device[4], '%Y-%m-%d %H:%M:%S').timestamp()) + 2419200 < int(datetime.now().timestamp()):
        db_conn.delete_device(device[0])
    if int(datetime.strptime(device[4], '%Y-%m-%d %H:%M:%S').timestamp()) + 43200 < int(datetime.now().timestamp()):
        db_conn.reset_ips(device[0])

