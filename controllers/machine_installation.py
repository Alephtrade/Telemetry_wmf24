from collections import deque
import nmap
import requests
import websocket
import json
from timezonefinder import TimezoneFinder
from datetime import datetime, timezone
import pytz
import logging
from controllers.db.models import WMFSQLDriver
import uuid

db_conn = WMFSQLDriver()


def test():
    nm = nmap.PortScanner()
    hosts = nm.scan(hosts='10.8.0.0/24', arguments='-sn')
    machine = []
    for host in hosts["scan"]:
        if host != "10.8.0.1":
            machine_response = require_info(host)
            url = f'https://wmf24.ru/api/get-coffee-machine-info/{machine_response["MachineName"]}'
            headers = {
                'Content-Type': 'application/json'
            }
            #response = requests.request("POST", url, headers=headers, data=json.dumps(machine_response))
            aleph_id = uuid.uuid4()
            latitude = 37.61556
            longitude = 55.75222
            finder = db_conn.find_device_by_aleph_id(aleph_id)
            if not finder:
                db_conn.create_device(str(aleph_id), str(utc_calc(latitude, longitude)), str(machine_response["ip"]), str(machine_response["ProductName"]), str(1))
            else:
                db_conn.update_device_info(str(aleph_id), str(utc_calc(latitude, longitude)), str(machine_response["ip"]), str(machine_response["ProductName"]), str(1))
            machine.append(machine_response)
            #ips.append(require(host))
    return machine

def require_info(ip):
    WS_URL = f'ws://{ip}:25000/'
    try:
        ws = websocket.create_connection(WS_URL, timeout=5)
    except Exception:
        ws = None
    request = json.dumps({'function': 'getMachineInfo'})
    print(request)
    print("------------------------------")
    logging.info(f"WMFMachineStatConnector: Sending {request}")
    ws.send(request)
    received_data = ws.recv()
    logging.info(f"WMFMachineStatConnector: Received {received_data}")
    received_data2 = deque(json.loads(received_data))
    formatted = {}
    for var in list(received_data2):
        for i in var:
            formatted[i] = var[i]
    formatted["ip"] = ip
    return formatted

def time_format(list):
    total = int(list[1]) * 60 * 60 + int(list[2]) * 60
    if list[0] == False:
        total = total - total * 2
    return total

def splitter(stroka, operator):
    return stroka.split(operator)

def utc_calc(latitude, longitude):
    global machine_time
    obj = TimezoneFinder()
    split_result = []
    times = []
    positive = True
    result = obj.timezone_at(lng=float(longitude), lat=float(latitude))
    dt_to_convert = datetime.utcnow().replace(tzinfo=timezone.utc)
    tz = datetime.strptime(datetime.now(pytz.timezone(result)).strftime("%z"), '%z').tzinfo
    timezone_machine = str(tz)
    utc_split = splitter(str(tz), "UTC")
    if utc_split[1] != "":
        plus_split = splitter(utc_split[1], "+")
        if 1 in dict(enumerate(plus_split)):
            time = splitter(plus_split[1], ":")
            split_result.append([positive, time[0], time[1]])
        else:
            minus_split = splitter(utc_split[1], "-")
            if 1 in dict(enumerate(minus_split)):
                positive = False
                time = splitter(minus_split[1], ":")
                split_result.append([positive, time[0], time[1]])
    else:
        split_result.append([True, 0, 0])
    for time in split_result:
        machine_time = time_format(time)

    return machine_time
