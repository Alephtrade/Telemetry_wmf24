import atexit
import json
import requests
import logging
from threading import Thread
from datetime import timedelta
from timeloop import Timeloop
from core.utils import initialize_logger, print_exception, get_env_mode, get_part_number_local
from wmf.models import WMFMachineErrorConnector, WMFMachineStatConnector
from settings import prod as settings
from db.models import WMFSQLDriver


WMF_URL = settings.WMF_DATA_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
tl = Timeloop()
initialize_logger('error_collector.log')
db_conn = WMFSQLDriver()
wmf_conn = WMFMachineErrorConnector()
wmf_part_number_operator = WMFMachineStatConnector()
try_to_get_part_number = get_part_number_local()
if try_to_get_part_number is None:
    try_to_get_part_number = wmf_part_number_operator.get_part_number()
Thread(target=wmf_conn.run_websocket, args=()).start()


def on_exit():
    try:
        wmf_conn.close()
        tl.stop()
    except Exception as ex:
        logging.error(f'error_collector on_exit: ERROR={ex}')
        logging.error(print_exception())


@tl.job(interval=timedelta(seconds=settings.ERROR_COLLECTOR_INTERVAL_SECONDS))
def send_errors():
    try:
        logging.info("error_collector send_errors: CALL")
        errors, request = '', ''
        unset_errors = db_conn.get_unsent_records()
        if unset_errors:
            for record in unset_errors:
                request = f'{WMF_URL}?code={try_to_get_part_number}&{DEFAULT_WMF_PARAMS}&error_id={record[1]}&date_start={record[2]}&date_end={record[3]}&duration={record[5]}&status={wmf_conn.get_status()}'
                response = requests.post(request)
                content = response.content.decode('utf-8')
                if record[3] is not None:
                    db_conn.set_report_sent(record[0])
                else:
                    db_conn.set_report_pre_sent(record[0])
                logging.info(f'error_collector send_errors: <= {response} {content}')
        else:
            unset_errors = db_conn.get_unsent_records_with_end_time()
            if unset_errors:
                for record in unset_errors:
                    request = f'{WMF_URL}?code={try_to_get_part_number}&{DEFAULT_WMF_PARAMS}&error_id={record[1]}&date_start={record[2]}&date_end={record[3]}&duration={record[5]}&status={wmf_conn.get_status()}'
                    response = requests.post(request)
                    content = response.content.decode('utf-8')
                    db_conn.set_report_sent(record[0])
                    logging.info(f'error_collector send_errors: <= {response} {content}')
            else:
                request = f'{WMF_URL}?code={try_to_get_part_number}&{DEFAULT_WMF_PARAMS}&error_id=0&status={wmf_conn.get_status()}'
                response = requests.post(request)
                logging.info(f'error_collector send_errors: nothing to send')
    except Exception as ex:
        logging.error(f'error_collector send_errors: ERROR={ex}, stacktrace: {print_exception()}')


tl.start()
logging.info('error_collector.py started and running...')
atexit.register(on_exit)
