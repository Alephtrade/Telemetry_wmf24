import sys
import websocket
from datetime import timedelta, datetime

sys.path.append("../../")
from db.models import WMFSQLDriver
from settings import prod as settings
from wmf.models import WMFMachineStatConnector
from core.utils import timedelta_str

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def get_clean_info():
    data = db_conn.get_last_cleaning_info()
    if data is not None:
        data_d = [
            {"last_general_cleaning_datetime": data[0]},
            {"general_cleaning_duration": data[1]},
            {"next_general_cleaning_datetime": data[2]},
            {"last_milk_cleaning_datetime": data[3]},
            {"general_milk_cleaning_duration": data[4]},
            {"next_milk_cleaning_datetime": data[5]},
            {"last_foamer_rising_datetime": data[6]},
            {"general_foamer_rising_duration": data[7]},
            {"next_foamer_rising_datetime": data[8]},
            {"last_milk_replacement_datetime": data[9]},
            {"general_milk_replacement_duration": data[10]},
            {"next_milk_replacement_datetime": data[11]},
            {"last_mixer_rinsing_datetime": data[12]},
            {"general_mixer_rinsing_duration": data[13]},
            {"next_mixer_rinsing_datetime": data[14]},
            {"last_milk_mixer_warm_rinsing_datetime": data[15]},
            {"general_milk_mixer_warm_rinsing_duration": data[16]},
            {"next_milk_mixer_warm_rinsing_datetime": data[17]},
            {"last_ffc_filter_replacement_datetime": data[18]},
            {"general_ffc_filter_replacement_duration": data[19]},
            {"next_ffc_filter_replacement_date": data[20]}
        ]
        return data_d
    else:
        return []

def get_main_data_stat():
    time_now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    wm_conn = WMFMachineStatConnector()
    ws = websocket.create_connection(WS_URL)
    if not wm_conn.ws:
        return False
    data = wm_conn.get_wmf_machine_info()
    summ = wm_conn.get_beverages_count()
    stoppage_time, wmf_error_time, time_count_default = timedelta(), timedelta(), timedelta(seconds=3600)
    stoppage_count, wmf_error_count = 0, 0
    unsent_records = db_conn.get_error_records(time_now, time_now + timedelta(hours=1))
    #return unsent_records
    for rec_id, error_code, start_time, end_time, error_text in unsent_records:
        if end_time:
            error_text = error_text if error_text else ''
            duration_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            time_count_default -= duration_time
            if error_code == -1:
                stoppage_count += 1
                stoppage_time += duration_time
            else:
                wmf_error_count += 1
                wmf_error_time += duration_time
    return {
        "summ": summ,
        "wmf_error_count": wmf_error_count,
        "wmf_error_time": timedelta_str(wmf_error_time),
        "time_worked": timedelta_str(time_count_default),
        "stoppage_count": stoppage_count,
        "stoppage_time": timedelta_str(stoppage_time)
    }
