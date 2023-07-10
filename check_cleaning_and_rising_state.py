import logging
import websocket
from datetime import datetime, timedelta
from db.models import WMFSQLDriver
from wmf.models import WMFMachineStatConnector
from settings import prod as settings
from core.utils import initialize_logger
from api.datastat.methods import get_main_data_stat

initialize_logger('check_cleaning_and_rising_state.log')
WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()
wm_conn = WMFMachineStatConnector()

def controller_manager(operator, last_column, duration_column, next_column):
    now_of_hour = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    record = db_conn.is_record_clean_or_rins(now_of_hour)
    if record is None:
        db_conn.create_clean_or_rins(now_of_hour)
    logging.info(f'PartNumber: {wm_conn.part_number}, curr_cleaning_duration: {operator}')
    if operator is not None:
        if operator['durationInSeconds'] is not None and int(operator['durationInSeconds']) != -1:
            prev_cleaning_duration = db_conn.get_last_clean_or_rins(duration_column)[1]
            logging.info(f'PartNumber: {wm_conn.part_number}, prev_cleaning_duration: {prev_cleaning_duration}')
            print(f'prev {prev_cleaning_duration}')
            print(f'durationInSeconds {operator["durationInSeconds"]}')

            if prev_cleaning_duration != operator['durationInSeconds']:
                    db_conn.save_clean_or_rins(duration_column, operator['durationInSeconds'])
                    if prev_cleaning_duration != 0 and prev_cleaning_duration != operator['durationInSeconds']:
                        print(f'new time {datetime.now()}')
                        print(db_conn.save_clean_or_rins(last_column, (datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')))
            if int(operator["dueInSeconds"]) is not None and int(operator["dueInSeconds"]) != -1:
                next_datetime = db_conn.get_last_clean_or_rins(next_column)[0]
                print(operator["dueInSeconds"])
                print(next_datetime)
                next_datetime = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() + int(operator["dueInSeconds"])))
                print(db_conn.save_clean_or_rins(next_column, next_datetime))
    else:
        return "machine is off"


print(wm_conn.get_system_cleaning_state(), wm_conn.get_milk_cleaning_state(), wm_conn.get_foamer_rinsing_state(), wm_conn.get_milk_replacement_state(), wm_conn.get_mixer_rinsing_state(), wm_conn.get_milk_mixer_warm_rinsing_state(), wm_conn.get_ffc_filter_replacement_state())
print(controller_manager(wm_conn.get_system_cleaning_state(), "last_general_cleaning_datetime", "general_cleaning_duration", "next_general_cleaning_datetime"))
controller_manager(wm_conn.get_milk_cleaning_state(), "last_milk_cleaning_datetime", "general_milk_cleaning_duration", "next_milk_cleaning_datetime")
controller_manager(wm_conn.get_foamer_rinsing_state(), "last_foamer_rising_datetime", "general_foamer_rising_duration", "next_foamer_rising_datetime")
controller_manager(wm_conn.get_milk_replacement_state(), "last_milk_replacement_datetime", "general_milk_replacement_duration", "next_milk_replacement_datetime")
controller_manager(wm_conn.get_mixer_rinsing_state(), "last_mixer_rinsing_datetime", "general_mixer_rinsing_duration", "next_mixer_rinsing_datetime")
controller_manager(wm_conn.get_milk_mixer_warm_rinsing_state(), "last_milk_mixer_warm_rinsing_datetime", "general_milk_mixer_warm_rinsing_duration", "next_milk_mixer_warm_rinsing_datetime")
controller_manager(wm_conn.get_ffc_filter_replacement_state(), "last_ffc_filter_replacement_datetime", "general_ffc_filter_replacement_duration", "next_ffc_filter_replacement_datetime")

get_main_data_stat()

