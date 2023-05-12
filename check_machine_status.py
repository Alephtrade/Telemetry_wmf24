import websocket
import logging
from db.models import WMFSQLDriver
from settings import prod as settings
from core.utils import initialize_logger


initialize_logger('check_machine_status.log')
db_driver = WMFSQLDriver()

status = None
try:
    ws = websocket.create_connection(settings.WS_URL, timeout=settings.WEBSOCKET_CONNECT_TIMEOUT)
    if ws.connected:
        ws.close()
        status = 1
except Exception:
    status = 0

logging.info(f'status is: {status}')
last_id, end_time = None, None
r = db_driver.get_error_last_stat_record('-1')
logging.info(f'last_stat_record: {r}')

if r:
    last_id, end_time = r
if status == 1 and (end_time is None and last_id is not None):
    logging.info(f'status is 1 and last_id is {last_id}, calling close_error_code_by_id({last_id})')
    db_driver.close_error_code_by_id(last_id)
elif status == 0 and (end_time is not None or last_id is None):
    logging.info(f'status is 0 and end_time is {end_time}, calling create_error_record(-1)')
    db_driver.create_error_record('-1', 'Кофемашина недоступна')

db_driver.close()
