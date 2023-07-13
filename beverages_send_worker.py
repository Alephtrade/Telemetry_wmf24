import ast
import logging
from core.utils import initialize_logger
from api.beverages import methods
from datetime import datetime, timedelta
from db.models import WMFSQLDriver
import json

db_driver = WMFSQLDriver()
initialize_logger('beverages_send_worker.py.log')

def get_reports_and_send_or_nothing():
    k = []
    time_to_send = None
    receive_data = db_driver.get_not_sended_beverages_log()
    if(receive_data == []):
        logging.info(f'NO DATA')
    else:
        for item in receive_data:
            logging.info(f'loop')
            time_to_send = item[2]
            k.append({"device_code": item[0]})
            k.append({"summ": item[1]})
            k.append({"time_to_send": item[2]})
            k.append({"time_fact_send": item[3]})
            k.append({"date_formed": item[4]})
            data_info = ast.literal_eval((item[5]))
            record_id = item[6]
            for item_info in data_info:
                k.append(item_info)
            next_time = datetime.strptime(time_to_send, '%Y-%m-%d %H:%M:%S')
            if datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())) > next_time:
                print(methods.Send_Statistics(json.dumps(k), record_id))
                logging.info(f'Send_Statistics db id - {record_id}')
            else:
                logging.info(f'wrong time to_sent - {next_time}')
    return True


print(get_reports_and_send_or_nothing())
