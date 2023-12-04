import atexit
import json
import requests
import logging
import threading
from threading import Thread
from datetime import timedelta
from timeloop import Timeloop
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.core.utils import initialize_logger, print_exception, get_env_mode, get_part_number_local
from controllers.wmf.models import WMFMachineErrorConnector
from controllers.settings import prod as settings
from controllers.db.models import WMFSQLDriver

threads = {}
aleph_id = Timeloop()
db_conn = WMFSQLDriver()


def worker(aleph_id, ip):
    WMF_URL = settings.WMF_DATA_URL
    print(ip)
    initialize_logger('error_collector.log')
    wmf_conn = WMFMachineErrorConnector(aleph_id, ip)
    Thread(target=wmf_conn.run_websocket, args=()).start()


    def on_exit():
        try:
            wmf_conn.close()
            aleph_id.stop()
        except Exception as ex:
            logging.error(f'error_collector on_exit: ERROR={ex}')
            logging.error(print_exception())


    @aleph_id.job(interval=timedelta(seconds=settings.ERROR_COLLECTOR_INTERVAL_SECONDS))
    def send_errors():
        try:
            logging.info("error_collector send_errors: CALL")
            errors, request = '', ''
            unset_errors = db_conn.get_unsent_records()
            if unset_errors:
                for record in unset_errors:
                    #request = f'{WMF_URL}?code={try_to_get_part_number}&error_id={record[1]}&date_start={record[2]}&date_end={record[3]}&duration={record[5]}&status={wmf_conn.get_status()}'
                    #response = requests.post(request)
                    #content = response.content.decode('utf-8')
                    if record[3] is not None:
                        db_conn.set_report_sent(record[0])
                    else:
                        db_conn.set_report_pre_sent(record[0])
                    #logging.info(f'error_collector send_errors: <= {response} {content}')
            else:
                unset_errors = db_conn.get_unsent_records_with_end_time()
                if unset_errors:
                    for record in unset_errors:
                        #request = f'{WMF_URL}?code={try_to_get_part_number}&error_id={record[1]}&date_start={record[2]}&date_end={record[3]}&duration={record[5]}&status={wmf_conn.get_status()}'
                        #response = requests.post(request)
                        #content = response.content.decode('utf-8')
                        db_conn.set_report_sent(record[0])
                        #logging.info(f'error_collector send_errors: <= {response} {content}')
                else:
                    #request = f'{WMF_URL}?code={try_to_get_part_number}&error_id=0&status={wmf_conn.get_status()}'
                    #response = requests.post(request)
                    logging.info(f'error_collector send_errors: nothing to send')
        except Exception as ex:
            logging.error(f'error_collector send_errors: ERROR={ex}, stacktrace: {print_exception()}')

    aleph_id.start()
    logging.info('error_collector.py started and running...')
    return "error_collector.py started and running..."
    atexit.register(on_exit)


db_conn = WMFSQLDriver()
devices = db_conn.get_devices()
result = []
for device in devices:
    result = worker(device[1], device[2])
    #print(Thread.getName(threads[device[1]]))

