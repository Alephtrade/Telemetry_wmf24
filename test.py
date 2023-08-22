import json
import logging
import websocket
import ast
from datetime import datetime, timedelta
import sys
import requests

sys.path.append("../../")
from db.models import WMFSQLDriver
from core.utils import initialize_logger, get_beverages_send_time, get_part_number_local
from settings import prod as settings
from wmf.models import WMFMachineStatConnector

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()


def worker():
    initialize_logger('beveragestatistics.log')
    wm_conn = WMFMachineStatConnector()
    fake_data = False
    summ = 0
    device_code = ""
    recipes = []
    date_to_send = get_beverages_send_time(last_send)
    date_formed = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
    try:
        ws = websocket.create_connection(WS_URL, timeout=5)
    except Exception:
        ws = None
        fake_data = True
        logging.info(f"error {wm_conn.ws}")
    if not wm_conn.ws:
        logging.info(f"error {wm_conn.ws}")
        fake_data = True
    else:
        request = json.dumps({'function': 'getBeverageStatistics'})
        ws.send(request)
        received_data = ws.recv()
        logging.info(f"{received_data}")
        if received_data is not None or received_data != []:
            try:
                with open('/root/wmf_1100_1500_5000_router/part_number.txt') as f:
                    part_number = f.read()
            except Exception:
                logging.info(f"part_number unknown")
            received_data = received_data.replace(']', '', 1)
            received_data = received_data + ', {"device_code" : ' + str(part_number) + '}]'
            logging.info(f"beveragestatistics: Received {received_data}")
            received = ast.literal_eval(received_data)
            for item in received:
                for k, item2 in item.items():
                    return item2
                    if (k.startswith("device_code")):
                        device_code = item2
                    if (k.startswith("TotalCountRcp")):
                        recipes.append(item)
            summ = wm_conn.get_beverages_count()
            ws.close()
    if fake_data:
        last_record = db_conn.get_last_beverages_log()
        if last_record is None:
            create_record = db_conn.create_beverages_log("0", "0", "1970-01-01 00:00:00", "1970-01-01 00:00:00",
                                                         "{}")
        else:
            create_record = db_conn.create_beverages_log(str(last_record[0]), str(last_record[1]),
                                                         str(last_record[2]), str(date_formed), str(last_record[5]))
    else:
        create_record = db_conn.create_beverages_log(str(device_code), str(summ), str(date_to_send),
                                                     str(date_formed), json.dumps(recipes))
        logging.info(f"result {create_record}")
    return create_record


print(worker())
