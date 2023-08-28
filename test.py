import sys
import websocket
import logging
import requests
import json
import ast
import socket
from datetime import timedelta, datetime
from api.beverages import methods


sys.path.append("../../")
from db.models import WMFSQLDriver
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()


def worker():
    k = []
    time_to_send = None
    receive_data = db_conn.get_not_sended_beverages_log()
    if(receive_data == []):
        print(f'NO DATA')
    else:
        for item in receive_data:
            print(f'loop')
            time_to_send = item[2]
            k.append({"device_code": item[0]})
            k.append({"summ": item[1]})
            k.append({"time_to_send": item[2]})
            k.append({"time_fact_send": item[3]})
            k.append({"date_formed": item[4]})
            data_info = ast.literal_eval(str(item[5]))
            record_id = item[6]
            for item_info in data_info:
                k.append(item_info)
            next_time = datetime.strptime(time_to_send, '%Y-%m-%d %H:%M:%S')
            if datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())) > next_time:
                print(methods.Send_Statistics(json.dumps(k), record_id))
                print(f'Send_Statistics db id - {record_id}')
            else:
                print(f'wrong time to_sent - {next_time}')


print(worker())
