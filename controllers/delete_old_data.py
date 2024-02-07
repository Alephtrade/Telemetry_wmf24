import sys
import websocket
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from datetime import datetime, timezone
from controllers.db.models import WMFSQLDriver

db_conn = WMFSQLDriver()

devices = db_conn.get_devices()
time_low_limit = datetime.fromtimestamp(int(datetime.now().timestamp() - 604800)).strftime("%Y-%m-%d %H:%M:%S")
db_conn.clean_data_tables(time_low_limit)

