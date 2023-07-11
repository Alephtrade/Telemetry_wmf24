import websocket
from datetime import timedelta, datetime
from db.models import WMFSQLDriver
from settings import prod as settings
from wmf.models import WMFMachineStatConnector
from core.utils import timedelta_int, get_beverages_send_time

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def get_main_data_stat():
    time_now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    wm_conn = WMFMachineStatConnector()
    ws = websocket.create_connection(WS_URL)
    if not wm_conn.ws:
        return False
    last_send = db_conn.get_last_machine_activity()
    if last_send is None:
        now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
        date_to_send = get_beverages_send_time(now)
        db_conn.create_machine_activity(time_now, date_to_send)
    else:
        date_to_send = get_beverages_send_time(last_send[0])
        db_conn.create_machine_activity(time_now, date_to_send)
    stoppage_time, wmf_error_time, time_count_default = timedelta(), timedelta(), timedelta(seconds=3600)
    stoppage_count, wmf_error_count = 0, 0
    unsent_records = db_conn.get_error_records(time_now - timedelta(hours=1), time_now)
    for rec_id, error_code, start_time, end_time, error_text in unsent_records:
        date_error_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        if date_error_start < (time_now - timedelta(hours=1)) and end_time is None:
            time_count_default = 0
            stoppage_count = 0
            wmf_error_count = 0
            if error_code == -1:
                stoppage_time = timedelta(seconds=3600)
                wmf_error_time = timedelta()
            else:
                stoppage_time = timedelta()
                wmf_error_time = timedelta(seconds=3600)
            break
        elif date_error_start >= (time_now - timedelta(hours=1)) and end_time is not None:
            duration_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            if error_code == -1:
                stoppage_count += 1
            else:
                wmf_error_count += 1
        elif end_time is not None:
            duration_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - (time_now - timedelta(hours=1))
            if error_code == -1:
                stoppage_count += 1
            else:
                wmf_error_count += 1
        else:
            duration_time = time_now - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        time_count_default -= duration_time
        if error_code == -1:
            stoppage_time += duration_time
        else:
            wmf_error_time += duration_time


    wmf_error_time = timedelta_int(wmf_error_time)
    time_count_default = timedelta_int(time_count_default)
    stoppage_time = timedelta_int(stoppage_time)
    if(wmf_error_time > 3600):
        wmf_error_time = 3600
    if(time_count_default < 0):
        time_count_default = 0
    if(stoppage_time > 3600):
        stoppage_time = 3600

    db_conn.save_machine_activity("time_worked", time_count_default)
    db_conn.save_machine_activity("wmf_error_count", wmf_error_count)
    db_conn.save_machine_activity("wmf_error_time", wmf_error_time)
    db_conn.save_machine_activity("stoppage_count", stoppage_count)
    db_conn.save_machine_activity("stoppage_time", stoppage_time)

    return {
        "time_worked": time_count_default,
        "wmf_error_count": wmf_error_count,
        "wmf_error_time": wmf_error_time,
        "stoppage_count": stoppage_count,
        "stoppage_time": stoppage_time
    }

get_main_data_stat()