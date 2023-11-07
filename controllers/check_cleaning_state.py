import logging
from controllers.datetime import datetime, timedelta
from controllers.db.models import WMFSQLDriver
from controllers.wmf.models import WMFMachineStatConnector
from controllers.core.utils import initialize_logger

initialize_logger('check_cleaning_state.log')
db_conn = WMFSQLDriver()
wm_conn = WMFMachineStatConnector()

curr_cleaning_duration = wm_conn.get_cleaning_duration()
#logging.info(f'PartNumber: {wm_conn.part_number}, curr_cleaning_duration: {curr_cleaning_duration}')
if curr_cleaning_duration is not None and curr_cleaning_duration != -1:
    prev_cleaning_duration = db_conn.get_last_record()[1]
    #logging.info(f'PartNumber: {wm_conn.part_number}, prev_cleaning_duration: {prev_cleaning_duration}')
    if prev_cleaning_duration != curr_cleaning_duration:
        db_conn.save_last_record('cleaning_duration', curr_cleaning_duration)
        if prev_cleaning_duration != 0:
            db_conn.save_last_record('cleaning_datetime', (datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'))

db_conn.close()
wm_conn.close()
