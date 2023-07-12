from api.beverages import methods
import logging
from core.utils import initialize_logger
from db.models import WMFSQLDriver
from datetime import datetime, timedelta

db_driver = WMFSQLDriver()

def are_need_to_create():
    initialize_logger('send_statistics.txt')
    logging.info(f"beveragestatistics: Received Create start")
    last_send = db_driver.get_last_beverages_log()
    if last_send is None:
        now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
        get = methods.Take_Create_Beverage_Statistics(now)
        print(get)
    else:
        get = methods.Take_Create_Beverage_Statistics(last_send[3])
        print(get)


pull = are_need_to_create()
logging.info(f"beveragestatistics: Received Create end {pull}")
