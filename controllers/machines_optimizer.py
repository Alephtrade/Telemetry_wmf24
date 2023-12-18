import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from datetime import datetime, timezone
from controllers.db.models import WMFSQLDriver

db_conn = WMFSQLDriver()

devices = db_conn.get_devices()
for device in devices:
    if int(datetime.strptime(device[4], '%Y-%m-%d %H:%M:%S').timestamp()) + 2419200 < int(datetime.now().timestamp()):
        db_conn.delete_device(device[0])
