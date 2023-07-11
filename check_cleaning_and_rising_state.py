import logging
from datetime import datetime, timedelta
from db.models import WMFSQLDriver
from wmf.models import WMFMachineStatConnector
from settings import prod as settings
from core.utils import initialize_logger

initialize_logger('check_cleaning_and_rising_state.log')
WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()
wm_conn = WMFMachineStatConnector()

def controller_manager(operator, alias):
    now_of_hour = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    record = db_conn.is_record_clean_or_rins(now_of_hour)
    if record is None:
        db_conn.create_clean_or_rins(now_of_hour, alias)
    logging.info(f'PartNumber: {wm_conn.part_number}, curr_cleaning_duration: {operator}')
    if operator is not None:
        if operator['durationInSeconds'] is not None and int(operator['durationInSeconds']) != -1:
            prev_cleaning_duration = db_conn.get_last_clean_or_rins("type_cleaning_duration")[1]
            logging.info(f'PartNumber: {wm_conn.part_number}, prev_cleaning_duration: {prev_cleaning_duration}')
            print(f'prev {prev_cleaning_duration}')
            print(f'durationInSeconds {operator["durationInSeconds"]}')
            if prev_cleaning_duration != operator['durationInSeconds']:
                    db_conn.save_clean_or_rins("type_cleaning_duration", operator['durationInSeconds'])
                    if prev_cleaning_duration == 0:
                        print(f'new time {datetime.now()}')
                        print(db_conn.save_clean_or_rins("type_last_cleaning_datetime", (datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')))
    else:
        return "machine is off"


print(wm_conn.get_system_cleaning_state(), wm_conn.get_milk_cleaning_state(), wm_conn.get_foamer_rinsing_state(), wm_conn.get_milk_replacement_state(), wm_conn.get_mixer_rinsing_state(), wm_conn.get_milk_mixer_warm_rinsing_state(), wm_conn.get_ffc_filter_replacement_state())
print(controller_manager(wm_conn.get_system_cleaning_state(), "general"))
controller_manager(wm_conn.get_milk_cleaning_state(), "general_milk")
controller_manager(wm_conn.get_foamer_rinsing_state(), "foamer")
controller_manager(wm_conn.get_milk_replacement_state(), "milk_replacement")
controller_manager(wm_conn.get_mixer_rinsing_state(), "general_mixer")
controller_manager(wm_conn.get_milk_mixer_warm_rinsing_state(), "milk_mixer_warm")
controller_manager(wm_conn.get_ffc_filter_replacement_state(), "ffc_filter")

