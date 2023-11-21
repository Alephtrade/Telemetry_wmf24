import logging
from datetime import datetime, timedelta
import sys
sys.path.append('./')
from controllers.db.models import WMFSQLDriver
from controllers.wmf.models import WMFMachineStatConnector
from controllers.core.utils import initialize_logger

initialize_logger('check_cleaning_state.log')
db_conn = WMFSQLDriver()
devices = db_conn.get_devices()
print(devices)
result = []
for device in devices:
    wm_conn = WMFMachineStatConnector(device[1], device[2])
    curr_cleaning_duration = wm_conn.get_cleaning_duration()
    print(curr_cleaning_duration)
    curr_cleaning_duration = 12
    #logging.info(f'PartNumber: {wm_conn.part_number}, curr_cleaning_duration: {curr_cleaning_duration}')
    if curr_cleaning_duration is not None and curr_cleaning_duration != -1:
        if db_conn.get_last_record() is not None and len(db_conn.get_last_record()) < 1:
            prev_cleaning_duration = db_conn.get_last_record()[1]
        else:
            prev_cleaning_duration = None
        #logging.info(f'PartNumber: {wm_conn.part_number}, prev_cleaning_duration: {prev_cleaning_duration}')
        print(prev_cleaning_duration)
        print(curr_cleaning_duration)
        if prev_cleaning_duration != curr_cleaning_duration:
            db_conn.save_last_record('cleaning_duration', curr_cleaning_duration)
            if prev_cleaning_duration != 0:
                db_conn.save_last_record('cleaning_datetime', (datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'))
    wm_conn.close()

db_conn.close()
