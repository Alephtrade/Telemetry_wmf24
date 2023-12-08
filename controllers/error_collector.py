import atexit
import json
import requests
import logging
import threading
from datetime import timedelta
from timeloop import Timeloop
import sys

sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.core.utils import initialize_logger, print_exception
from controllers.wmf.models import WMFMachineErrorConnector
from controllers.settings import prod as settings
from controllers.db.models import WMFSQLDriver

threads = {}
WMF_URL = settings.WMF_DATA_URL


def worker(tl_ident, aleph_id, ip):
    print(ip)
    initialize_logger('error_collector.log')
    tl_ident.start()
    return tl_ident.is_alive()


db_conn = WMFSQLDriver()
devices = db_conn.get_devices()
result = []
for device in devices:
    wmf_conn = WMFMachineErrorConnector(device[1], device[2])
    if threading.Thread(target=wmf_conn.run_websocket, name=device[1]).is_alive():
        print("ALIVE")
    tl_ident = threading.Thread(target=wmf_conn.run_websocket, name=device[1])
    result = worker(tl_ident, device[1], device[2])
    print(result)
    print(threading.active_count())
    print(threading.enumerate())


def on_exit():
    try:
        wmf_conn.close()
        tl_ident.stop()
    except Exception as ex:
        logging.error(f'error_collector on_exit: ERROR={ex}')
        logging.error(print_exception())

        @tl_ident.job(interval=timedelta(seconds=settings.ERROR_COLLECTOR_INTERVAL_SECONDS))
        def send_errors():
            try:
                logging.info("error_collector send_errors: CALL")
                errors, request = '', ''
                unset_errors = db_conn.get_unsent_records(device[1])
                if unset_errors:
                    for record in unset_errors:
                        request = f'{WMF_URL}?device={device[1]}&error_id={record[1]}&date_start={record[2]}&date_end={record[3]}&duration={record[5]}&status={wmf_conn.get_status()}'
                        print(request)
                        response = requests.post(request)
                        content = response.content.decode('utf-8')
                        if record[3] is not None:
                            db_conn.set_report_sent(record[0])
                        else:
                            db_conn.set_report_pre_sent(record[0])
                        logging.info(f'error_collector send_errors: <= {response} {content}')
                else:
                    unset_errors = db_conn.get_unsent_records_with_end_time(device[1])
                    if unset_errors:
                        for record in unset_errors:
                            request = f'{WMF_URL}?device={device[1]}&error_id={record[1]}&date_start={record[2]}&date_end={record[3]}&duration={record[5]}&status={wmf_conn.get_status()}'
                            print(request)
                            response = requests.post(request)
                            content = response.content.decode('utf-8')
                            db_conn.set_report_sent(record[0])
                            logging.info(f'error_collector send_errors: <= {response} {content}')
                    else:
                        request = f'{WMF_URL}?device={device[1]}&error_id=0&status={wmf_conn.get_status()}'
                        print(request)
                        response = requests.post(request)
                        logging.info(f'error_collector send_errors: nothing to send')
            except Exception as ex:
                logging.error(f'error_collector send_errors: ERROR={ex}, stacktrace: {print_exception()}')

        # tl.start()
        logging.info('error_collector.py started and running...')
        atexit.register(on_exit)
        return tl_ident.is_alive()
