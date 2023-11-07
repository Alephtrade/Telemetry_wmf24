import sys
import websocket
import logging
import requests
import json
import ast
import socket
from datetime import timedelta, datetime
from controllers.api.beverages import methods
from timezonefinder import TimezoneFinder
from datetime import datetime, timezone
import pytz
sys.path.append("../../")
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.wmf.models import WMFMachineStatConnector, WMFMachineErrorConnector
from controllers.core.utils import initialize_logger, print_exception, get_env_mode, get_part_number_local, get_beverages_send_time, timedelta_int
#
#
#WMF_URL = settings.WMF_DATA_URL
#WS_URL = settings.WS_URL
#DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()
#wmf_conn = WMFMachineErrorConnector()
#wmf2_conn = WMFMachineStatConnector()

#def worker():
#    time_now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
#    prev_hour = time_now - timedelta(hours=1)
#    unsent_records = db_conn.get_error_records(prev_hour, time_now)
#    unsent_disconnect_records = db_conn.get_all_error_records_by_code(prev_hour, time_now, "-1")
#    #return print(unsent_disconnect_records)
#    print(unsent_records)
#    date_end_prev_error = prev_hour
#    wmf_error_time = 0
#    per_error_time = timedelta()
#    total_disconnect_time = 0
#    disconnect_time = timedelta()
#    for rec_id, error_code, start_time, end_time, error_text in unsent_records:
#        #print(start_time)
#        if(type(start_time) is not datetime):
#            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
#        if (type(end_time) is not datetime):
#            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
#        if start_time < date_end_prev_error:
#            start_time = date_end_prev_error
#        if end_time is None or end_time > time_now:
#            end_time = time_now
#        if end_time < date_end_prev_error:
#            end_time = date_end_prev_error
#        for disconnect_rec_id, disconnect_error_code, disconnect_start_time, disconnect_end_time, disconnect_error_text in unsent_disconnect_records:
#            # print(start_time)
#            if (type(disconnect_start_time) is not datetime):
#                disconnect_start_time = datetime.strptime(disconnect_start_time, '%Y-%m-%d %H:%M:%S')
#            if (type(disconnect_end_time) is not datetime and disconnect_end_time is not None):
#                disconnect_end_time = datetime.strptime(disconnect_end_time, '%Y-%m-%d %H:%M:%S')
#            if disconnect_start_time < start_time: # 3.4.1
#                disconnect_start_time = prev_hour
#            if disconnect_end_time is None or disconnect_end_time > time_now: # 3.4.2
#                disconnect_end_time = time_now
#            if start_time < disconnect_start_time and end_time > disconnect_end_time: # 3.4.3
#                start_time = disconnect_end_time - (disconnect_start_time - start_time)
#            else:
#                if start_time >= disconnect_start_time and start_time < disconnect_end_time: # 3.4.3.1
#                    start_time = disconnect_end_time
#                if end_time > disconnect_start_time and end_time < disconnect_end_time: # 3.4.3.2
#                    end_time = disconnect_start_time
#            if disconnect_start_time < time_now:
#                disconnect_start_time = prev_hour
#            if disconnect_end_time is None or disconnect_end_time > time_now:
#                disconnect_end_time = time_now
#            disconnect_time = disconnect_end_time - disconnect_start_time
#            disconnect_time = timedelta_int(disconnect_time)
#            if disconnect_time < 0:
#                disconnect_time = 0
#            total_disconnect_time += disconnect_time
#        per_error_time = end_time - start_time
#        per_error_time = timedelta_int(per_error_time)
#        if per_error_time < 0:
#            per_error_time = 0
#        wmf_error_time += per_error_time
#        date_end_prev_error = end_time


#    print({
#        "wmf_error_time": wmf_error_time,
#        "disconnect_time": disconnect_time
#    })

def worker():
    #ws = websocket.create_connection(WS_URL, timeout=5)
    #request = json.dumps({'function': 'deleteRecipe'})
    #ws.send(request)
    #received_data = ws.recv()
    #print(received_data)
    obj = TimezoneFinder()
    latitude = 37.6156
    longitude = 55.7522
    result = obj.timezone_at(lng=latitude, lat=longitude)
#
    d = []
    dt_to_convert = datetime.utcnow().replace(tzinfo=timezone.utc)
    d.append(datetime.now(pytz.timezone(result)).strftime("%m/%d/%Y, %H:%M:%S %z"))
    d.append(dt_to_convert)
    #tz = datetime.strptime(datetime.now(pytz.timezone(result)).strftime("%z"), '%z').tzinfo
    #d.append(dt_to_convert.astimezone(tz))
    tz = datetime.strptime('+0600', '%z').tzinfo
    d.append(dt_to_convert.astimezone(tz).strftime("%m/%d/%Y, %H:%M:%S %z"))
    new_date = str(dt_to_convert.astimezone(tz))
    return str(tz)
    return new_date

#worker()
