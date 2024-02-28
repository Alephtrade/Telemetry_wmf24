import websocket
import logging
import requests
import json
import time
from datetime import timedelta, datetime, date
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.core.utils import timedelta_int, initialize_logger, get_beverages_send_time
from controllers.api.beverages import methods

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def get_main_clean_stat(device):
    start_time = None
    end_time = None
    print(device)
    #initialize_logger('controller_cleaning_statistic_creator.py.log')
    time_now = datetime.fromtimestamp(int(datetime.now().timestamp() // (60 * 60) * 60 * 60))
    time_now_to_db_save = datetime.fromtimestamp(int(datetime.now().timestamp() // (60 * 60) * 60 * 60 - 1))

    prev_hour = time_now - timedelta(hours=1)
    #get_last_data_statistics = db_conn.get_last_data_statistics()
    #if get_last_data_statistics is not None and len(get_last_data_statistics) > 0:
    #    date_to_send = get_beverages_send_time(get_last_data_statistics[0])
    #else:
    #date_to_send = get_beverages_send_time(time_now)
    date_to_send = get_beverages_send_time(time_now)
    #print(date_to_send)
    db_conn.create_data_statistics(device[1], time_now_to_db_save, date_to_send)
    last_bev_rec_id = db_conn.get_last_data_statistics_id(device[1])[0]
    #print("last id")
    #print(last_bev_rec_id)
    unsent_records = db_conn.get_error_records(prev_hour, time_now, device[1])
    #print({"Ошибки": unsent_records})
    #print({prev_hour, time_now, device[1]})
    unsent_disconnect_records = db_conn.get_all_error_records_by_code(device[1], prev_hour, time_now, "-1")
    #print({"Ошибки -1": unsent_disconnect_records})
    date_end_prev_error = prev_hour
    wmf_error_time = 0
    per_error_time = timedelta()
    total_disconnect_time = 0
    disconnect_time = timedelta()
    wmf_error_count = 0
    disconnect_count = 0
    for rec_id, error_code, start_time, end_time in unsent_records:
        print({"Ошибки": unsent_records})
        if type(start_time) is not datetime and start_time is not None:
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        if type(end_time) is not datetime and end_time is not None:
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        if end_time is None or end_time > time_now:
            end_time = time_now
        if start_time < date_end_prev_error:
            start_time = date_end_prev_error
        if end_time < date_end_prev_error:
            end_time = date_end_prev_error
        per_error_time = end_time - start_time
        per_error_time = timedelta_int(per_error_time)
        print({"db_id", rec_id})
        print({"time", per_error_time})
        print(wmf_error_time)
        if per_error_time < 0:
            per_error_time = 0
        wmf_error_time += per_error_time
        wmf_error_count += 1
        date_end_prev_error = end_time
    for disconnect_rec_id, disconnect_error_code, disconnect_start_time, disconnect_end_time in unsent_disconnect_records:
        if start_time is None:
            start_time = prev_hour
        if end_time is None:
            end_time = time_now
        print({"Остановки": unsent_disconnect_records})
        if type(disconnect_start_time) is not datetime and disconnect_start_time is not None:
            disconnect_start_time = datetime.strptime(disconnect_start_time, '%Y-%m-%d %H:%M:%S')
        if type(disconnect_end_time) is not datetime and disconnect_end_time is not None:
            disconnect_end_time = datetime.strptime(disconnect_end_time, '%Y-%m-%d %H:%M:%S')
        if disconnect_start_time < start_time:  # 3.4.1
            disconnect_start_time = prev_hour
        if disconnect_end_time is None or disconnect_end_time > time_now:  # 3.4.2
            disconnect_end_time = time_now
        if start_time < disconnect_start_time and end_time > disconnect_end_time:  # 3.4.3
            start_time = disconnect_end_time - (disconnect_start_time - start_time)
        else:
            if disconnect_start_time <= start_time < disconnect_end_time:  # 3.4.3.1
                start_time = disconnect_end_time
            if disconnect_start_time < end_time < disconnect_end_time:  # 3.4.3.2
                end_time = disconnect_start_time
        #if disconnect_start_time < time_now:
        #    disconnect_start_time = prev_hour
        if disconnect_end_time is None or disconnect_end_time > time_now:
            disconnect_end_time = time_now
        print({disconnect_end_time, disconnect_start_time})
        disconnect_time = int(disconnect_end_time.timestamp()) - int(disconnect_start_time.timestamp())
        #disconnect_time = timedelta_int(disconnect_time)
        total_disconnect_time += disconnect_time
        print({"db_id", disconnect_rec_id})
        print({"time", disconnect_time})
        print(total_disconnect_time)
        disconnect_count += 1


        date_end_prev_error = end_time

    wmf_work_time = 3600 - wmf_error_time - total_disconnect_time

    if wmf_error_time > 3600:
        wmf_error_time = 3600
    if wmf_work_time < 0:
        wmf_work_time = 0
    if total_disconnect_time > 3600:
        total_disconnect_time = 3600
    #print("result 1")
    #print({"time_worked": int(wmf_work_time),
    #       "wmf_error_count": int(wmf_error_count),
    #       "wmf_error_time": int(wmf_error_time),
    #       "stoppage_count": int(disconnect_count),
    #       "stoppage_time": int(total_disconnect_time)})
    db_conn.save_data_statistics(str(device[1]), "time_worked", wmf_work_time, last_bev_rec_id)
    db_conn.save_data_statistics(str(device[1]), "wmf_error_count", wmf_error_count, last_bev_rec_id)
    db_conn.save_data_statistics(str(device[1]), "wmf_error_time", wmf_error_time, last_bev_rec_id)
    db_conn.save_data_statistics(str(device[1]), "stoppage_count", disconnect_count, last_bev_rec_id)
    db_conn.save_data_statistics(str(device[1]), "stoppage_time", total_disconnect_time, last_bev_rec_id)

    #logging.info(f'time_worked {wmf_work_time}, wmf_error_count {wmf_error_count}, wmf_error_time {wmf_error_time}, stoppage_count {disconnect_count}, stoppage_time: {total_disconnect_time}')
    #print("result 2")
    #print(
    #    {
    #        "wmf_work_time": wmf_work_time,
    #        "wmf_error_count": wmf_error_count,
    #        "wmf_error_time": wmf_error_time,
    #        "disconnect_count": disconnect_count,
    #        "disconnect_time": total_disconnect_time
    #    })
    return True


def get_service_statistics(device):
    #initialize_logger('getServiceStatistics.log')
    date_today = date.today()
    #logging.info(f"COFFEE_MACHINE: today date in service_stat {date_today}")

    #print(date_today)
    try:
        WS_IP = f'ws://{device[2]}:25000/'
        ws = websocket.create_connection(WS_IP, timeout=5)
    except Exception:
        ws = None
        #logging.info(f"error {ws}")
        return False
    actual = db_conn.get_last_service_statistics(device[1], date_today)
    #logging.info(f"COFFEE_MACHINE: last service_stat record {actual}")
    if actual is None:
        # print("create")
        record = db_conn.create_service_record(device[1], date_today)
        #logging.info(f"COFFEE_MACHINE: created record service_stat {record}")
    else:
        if actual[2] == "0":
            # print("form")
            request = json.dumps({'function': 'getServiceStatistics'})
            #logging.info(f"COFFEE_MACHINE: Sending {request}")
            ws.send(request)
            received_data = ws.recv()
            #logging.info(f"servicestatistics: Received {received_data}")
            #text_file = open("response.txt", "a")
            #text_file.write(received_data)
            ts = time.time()
            int_ts = int(ts)
            received_data = received_data.replace(']', '', 1)
            received_data = received_data + ', {"device" : "' + str(device[1]) + '"}, {"timestamp_create" : ' + str(int_ts) + '}]'
            #print(received_data)
            url = "https://backend.wmf24.ru/api/servicestatistics"
            headers = {
                'Content-Type': 'application/json',
                'Serverkey': db_conn.get_encrpt_key()[0]
                    }
            #print(received_data)
            response = requests.request("POST", url, headers=headers, data=received_data)
            #logging.info(f"servicestatistics: GET response: {response.text}")
            db_conn.save_status_service_statistics(actual[0], "date_fact_send", str(datetime.fromtimestamp(int((datetime.now()).timestamp()))))
            db_conn.save_status_service_statistics(actual[0], "is_sent", "1")
            ws.close()
            #print(response.text)
            return response

def are_need_to_create(device):
    #initialize_logger('beveragestatistics.log')
    #logging.info(f"beveragestatistics: Received Create start")
    last_send = db_conn.get_last_beverages_log(device[1])
    #logging.info(f"{last_send}")
    if last_send is None:
        now = datetime.fromtimestamp(int((datetime.now()).timestamp()))
        get = methods.Take_Create_Beverage_Statistics(now, device)
        #logging.info(f"beveragestatistics: Sending {get}")
        #logging.info(f" last_send unknown")
        #logging.info(f"{get}")
    else:
        get = methods.Take_Create_Beverage_Statistics(last_send[3], device)
        #logging.info(f"beveragestatistics: Sending {get}")
        #logging.info(f"{get}")
    #print(get)
    return get


devices = db_conn.get_devices()
for device in devices:
#    print(device[2])
    are_need_to_create(device)
    get_service_statistics(device)
    get_main_clean_stat(device)
