import websocket
import logging
import requests
import json
import time
from datetime import timedelta, datetime, date
import sys
sys.path.append('./')
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.core.utils import timedelta_int, get_beverages_send_time, initialize_logger, get_part_number_local
from controllers.api.beverages import methods

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def get_main_clean_stat(device):
    initialize_logger('controller_cleaning_statistic_creator.py.log')
    time_now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    prev_hour = time_now - timedelta(hours=1)
    #get_last_data_statistics = db_conn.get_last_data_statistics()
    #if get_last_data_statistics is not None and len(get_last_data_statistics) > 0:
    #    date_to_send = get_beverages_send_time(get_last_data_statistics[0])
    #else:
    #date_to_send = get_beverages_send_time(time_now)
    date_to_send = time_now
    print(date_to_send)
    db_conn.create_data_statistics(time_now, date_to_send)
    unsent_records = db_conn.get_error_records(prev_hour, time_now)
    unsent_disconnect_records = db_conn.get_all_error_records_by_code(prev_hour, time_now, "-1")
    date_end_prev_error = prev_hour
    wmf_error_time = 0
    per_error_time = timedelta()
    total_disconnect_time = 0
    disconnect_time = timedelta()
    wmf_error_count = 0
    disconnect_count = 0
    for rec_id, error_code, start_time, end_time, error_text in unsent_records:
        # print(start_time)
        if (type(start_time) is not datetime):
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        if (type(end_time) is not datetime):
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        if start_time < date_end_prev_error:
            start_time = date_end_prev_error
        if end_time is None or end_time > time_now:
            end_time = time_now
        if end_time < date_end_prev_error:
            end_time = date_end_prev_error
        for disconnect_rec_id, disconnect_error_code, disconnect_start_time, disconnect_end_time, disconnect_error_text in unsent_disconnect_records:
            # print(start_time)
            if (type(disconnect_start_time) is not datetime):
                disconnect_start_time = datetime.strptime(disconnect_start_time, '%Y-%m-%d %H:%M:%S')
            if (type(disconnect_end_time) is not datetime and disconnect_end_time is not None):
                disconnect_end_time = datetime.strptime(disconnect_end_time, '%Y-%m-%d %H:%M:%S')
            if disconnect_start_time < start_time:  # 3.4.1
                disconnect_start_time = prev_hour
            if disconnect_end_time is None or disconnect_end_time > time_now:  # 3.4.2
                disconnect_end_time = time_now
            if start_time < disconnect_start_time and end_time > disconnect_end_time:  # 3.4.3
                start_time = disconnect_end_time - (disconnect_start_time - start_time)
            else:
                if start_time >= disconnect_start_time and start_time < disconnect_end_time:  # 3.4.3.1
                    start_time = disconnect_end_time
                if end_time > disconnect_start_time and end_time < disconnect_end_time:  # 3.4.3.2
                    end_time = disconnect_start_time
            if disconnect_start_time < time_now:
                disconnect_start_time = prev_hour
            if disconnect_end_time is None or disconnect_end_time > time_now:
                disconnect_end_time = time_now
            disconnect_time = disconnect_end_time - disconnect_start_time
            disconnect_time = timedelta_int(disconnect_time)
            if disconnect_time < 0:
                disconnect_time = 0
            total_disconnect_time += disconnect_time
            disconnect_count += 1
        per_error_time = end_time - start_time
        per_error_time = timedelta_int(per_error_time)
        if per_error_time < 0:
            per_error_time = 0
        wmf_error_time += per_error_time
        wmf_error_count += 1
        date_end_prev_error = end_time

    wmf_work_time = 3600 - wmf_error_time - total_disconnect_time

    if wmf_error_time > 3600:
        wmf_error_time = 3600
    if wmf_work_time < 0:
        wmf_work_time = 0
    if total_disconnect_time > 3600:
        total_disconnect_time = 3600

    #print({"time_worked", time_count_default, "wmf_error_count", wmf_error_count, "wmf_error_time", wmf_error_time, "stoppage_count", stoppage_count, "stoppage_time", stoppage_time})
    db_conn.save_data_statistics(device[1], "time_worked", wmf_work_time)
    db_conn.save_data_statistics(device[1], "wmf_error_count", wmf_error_count)
    db_conn.save_data_statistics(device[1], "wmf_error_time", wmf_error_time)
    db_conn.save_data_statistics(device[1], "stoppage_count", disconnect_count)
    db_conn.save_data_statistics(device[1], "stoppage_time", total_disconnect_time)

    logging.info(f'time_worked {wmf_work_time}, wmf_error_count {wmf_error_count}, wmf_error_time {wmf_error_time}, stoppage_count {disconnect_count}, stoppage_time: {total_disconnect_time}')
    print(
        {
            "wmf_work_time": wmf_work_time,
            "wmf_error_count": wmf_error_count,
            "wmf_error_time": wmf_error_time,
            "disconnect_count": disconnect_count,
            "disconnect_time": total_disconnect_time
        })
    return True

    
def get_service_statistics(device):
    initialize_logger('getServiceStatistics.log')
    date_today = date.today()
    logging.info(f"COFFEE_MACHINE: today date in service_stat {date_today}")

    #print(date_today)
    try:
        WS_IP = f'ws://{device[2]}:25000/'
        ws = websocket.create_connection(WS_IP, timeout=5)
    except Exception:
        ws = None
        logging.info(f"error {ws}")
        return False
    actual = db_conn.get_last_service_statistics(device[1], date_today)
    logging.info(f"COFFEE_MACHINE: last service_stat record {actual}")
    #print(actual)
    if actual is None:
        #print("create")
        record = db_conn.create_service_record(device[1], date_today)
        logging.info(f"COFFEE_MACHINE: created record service_stat {record}")
        actual = db_conn.get_last_service_statistics(device[1], date_today)
    else:
        if actual[2] == "0":
            #print("form")
            request = json.dumps({'function': 'getServiceStatistics'})
            logging.info(f"COFFEE_MACHINE: Sending {request}")
            ws.send(request)
            received_data = ws.recv()
            logging.info(f"servicestatistics: Received {received_data}")
            part_number = get_part_number_local()
            logging.info(f"COFFEE_MACHINE: Received {part_number}")
            text_file = open("response.txt", "a")
            text_file.write(received_data)
            ts = time.time()
            int_ts = int(ts)
            received_data = received_data.replace(']', '', 1)
            received_data = received_data + ', {"device_code" : ' + str(part_number) + '}, {"timestamp_create" : ' + str(int_ts) + '}]'

            url = "https://wmf24.ru/api/servicestatistics"
            headers = {
                'Content-Type': 'application/json'
            }
            print(received_data)
            response = requests.request("POST", url, headers=headers, data=received_data)
            print(response.text)
            logging.info(f"servicestatistics: GET response: {response.text}")
            db_conn.save_status_service_statistics(actual[0], "date_fact_send", str(datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))))
            db_conn.save_status_service_statistics(actual[0], "is_sent", "1")
            ws.close()
            return True

def are_need_to_create(device):
    initialize_logger('beveragestatistics.log')
    logging.info(f"beveragestatistics: Received Create start")
    last_send = db_conn.get_last_beverages_log()
    logging.info(f"{last_send}")
    iter = 0
    if last_send is None:
        now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
        get = methods.Take_Create_Beverage_Statistics(now, device)
        if get is None:
            get = methods.Take_Create_Beverage_Statistics(now, device)
            if get is None:
                get = methods.Take_Create_Beverage_Statistics(now, device)
                if get is None:
                    get = methods.Take_Create_Beverage_Statistics(now, device)
        logging.info(f"beveragestatistics: Sending {get}")
        logging.info(f" last_send unknown")
        logging.info(f"{get}")
    else:
        get = methods.Take_Create_Beverage_Statistics(last_send[3], device)
        if get is None:
            get = methods.Take_Create_Beverage_Statistics(last_send[3], device)
            if get is None:
                get = methods.Take_Create_Beverage_Statistics(last_send[3], device)
                if get is None:
                    get = methods.Take_Create_Beverage_Statistics(last_send[3], device)
        logging.info(f"beveragestatistics: Sending {get}")
        logging.info(f"{get}")
    print(get)
    return get


devices = db_conn.get_devices()
for device in devices:
    print(device[2])
    print(are_need_to_create(device))
    print(get_service_statistics(device))
    print(get_main_clean_stat(device))
