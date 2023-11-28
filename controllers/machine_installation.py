from collections import deque
import nmap
import requests
import websocket
import json
import logging


def test():
    return require_info("10.8.0.6")[0]["MachineName"]
    nm = nmap.PortScanner()
    hosts = nm.scan(hosts='10.8.0.0/24', arguments='-sn')
    ips = []
    for host in hosts["scan"]:
        if host != "10.8.0.1":
            machine = []
            response = require(host)
            url = "https://wmf24.ru/api/get-coffee-machine-info/"
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=json.dumps(data_for_request))
            machine.append({require(host)})
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
