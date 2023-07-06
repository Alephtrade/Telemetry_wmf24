import sys

sys.path.append("../../")
from db.models import WMFSQLDriver
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()


def get_clean_info():
    data = db_conn.get_last_cleaning_info()
    return data
    data_d = [
        {"last_general_cleaning_datetime": data[0]},
        {"general_cleaning_duration": data[1]},
        {"next_general_cleaning_datetime": data[2]},
        {"last_milk_cleaning_datetim": data[3]},
        {"general_milk_cleaning_duratio": data[4]},
        {"next_milk_cleaning_datetim": data[5]},
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
