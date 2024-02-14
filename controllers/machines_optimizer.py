import sys
import websocket
import requests
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from datetime import datetime, timezone
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings

db_conn = WMFSQLDriver()
WMF_URL = settings.WMF_DATA_URL



def status_send_anyway(status_machine, device_aleph_id):
    data = {'aleph_id': device_aleph_id, "status": status_machine}
    url = "https://backend.wmf24.ru/api/km_status"
    headers = {
        'Content-Type': 'application/json',
        'Serverkey': db_conn.get_encrpt_key()[0]
    }
    response = requests.request("POST", url, headers=headers, json=data)


def send_errors():
    devices_list = db_conn.get_devices()
    for device_item in devices_list:
        try:
            #logging.info("error_collector send_errors: CALL")
            errors, request = '', ''
            unset_errors = db_conn.get_unsent_records(device_item[1])
            print(unset_errors)
            if unset_errors:
                for record in unset_errors:
                    print(record)
                    request = f'{WMF_URL}?device={device_item[1]}&error_id={record[1]}&date_start={record[2]}&date_end={record[3]}&duration={record[4]}&status={wmf_conn.get_status()}'
                    print("errorrrrrrrrrrrrrrrrrrrrr")
                    print(request)
                    response = requests.post(request)
                    content = response.content.decode('utf-8')
                    if record[3] is not None:
                        db_conn.set_report_sent(record[0])
                    else:
                        db_conn.set_report_pre_sent(record[0])
                    #logging.info(f'error_collector send_errors: <= {response} {content}')
            else:
                unset_errors = db_conn.get_unsent_records_with_end_time(device_item[1])
                if unset_errors:
                    for record in unset_errors:
                        request = f'{WMF_URL}?device={device_item[1]}&error_id={record[1]}&date_start={record[2]}&date_end={record[3]}&duration={record[4]}&status={wmf_conn.get_status()}'
                        print("72")
                        print(request)
                        response = requests.post(request)
                        content = response.content.decode('utf-8')
                        db_conn.set_report_sent(record[0])
                        #logging.info(f'error_collector send_errors: <= {response} {content}')
                    #logging.info(f'error_collector send_errors: nothing to send')
        except Exception as ex:
            print(ex)
            #logging.error(f'error_collector send_errors: ERROR={ex}, stacktrace: {print_exception()}')



devices = db_conn.get_devices()
for device in devices:
    WS_URL = f'ws://{device[2]}:25000/'
    try:
        ws = websocket.create_connection(WS_URL, timeout=5)
        status = 1
    except Exception:
        ws = False
        status = 0
    last_record = db_conn.get_error_last_stat_record("-1", device[1])
    print(last_record)
    if last_record[1] and last_record[1] is not None:
        print(last_record[1])
        db_conn.create_error_record(device[1], '-1')
    status_send_anyway(status, device[1])
    send_errors()
    if ws == False:
        db_conn.reset_ips(device[1])
    if int(datetime.strptime(device[4], '%Y-%m-%d %H:%M:%S').timestamp()) + 2419200 < int(
            datetime.now().timestamp()):
        db_conn.delete_device(device[0])
    if int(datetime.strptime(device[4], '%Y-%m-%d %H:%M:%S').timestamp()) + 43200 < int(datetime.now().timestamp()):
        db_conn.reset_ips(device[0])


