import atexit
import requests
import logging
from threading import Thread
from datetime import timedelta
from timeloop import Timeloop
from core.utils import initialize_logger, print_exception, get_env_mode
from wmf.models import WMFMachineErrorConnector
if get_env_mode() == 'prod':
    from settings import prod as settings
else:
    from settings import test as settings


WMF_URL = settings.WMF_DATA_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
tl = Timeloop()
initialize_logger('error_collector.log')

wmf_conn = WMFMachineErrorConnector()
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
        if len(wmf_conn.current_errors) > 0 and wmf_conn.current_errors != wmf_conn.previous_errors:
            errors = ','.join(str(err) for err in wmf_conn.current_errors)
        elif len(wmf_conn.current_errors) == 0:
            errors = '0'
        if errors:
            request = f'{WMF_URL}?code={wmf_conn.part_number}&{DEFAULT_WMF_PARAMS}&error_id={errors}&status={wmf_conn.get_status()}'
        elif wmf_conn.get_status() == 0:
            request = f'{WMF_URL}?code={wmf_conn.part_number}&{DEFAULT_WMF_PARAMS}&error_id=0&status=0'
        if request:
            logging.info(f'error_collector send_errors: => {request}')
            response = requests.post(request, timeout=settings.REQUEST_TIMEOUT)
            content = response.content.decode('utf-8')
            if len(response.content) > settings.LOGGER_TEXT_LIMIT:
                content = content[:settings.LOGGER_TEXT_LIMIT]
            logging.info(f'error_collector send_errors: <= {response} {content}')
        wmf_conn.previous_errors = wmf_conn.current_errors.copy()
        # wmf_conn.db_driver.save_last_record('previous_errors', json.dumps(list(wmf_conn.previous_errors)))
    except Exception as ex:
        logging.error(f'error_collector send_errors: ERROR={ex}, stacktrace: {print_exception()}')


tl.start()
logging.info('error_collector.py started and running...')
atexit.register(on_exit)
