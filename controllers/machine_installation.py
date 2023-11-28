import nmap
import requests
import websocket
import json
import logging


def test():
    nm = nmap.PortScanner()
    hosts = nm.scan(hosts='10.8.0.0/24', arguments='-sn')
    ips = []
    for host in hosts["scan"]:
        if host != "10.8.0.1":
            machine = []
            machine.append({"IP": host})
            machine.append({"BODY": require(host)})
        #ips.append(require(host))
            return machine

def require(ip):
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
    return received_data
