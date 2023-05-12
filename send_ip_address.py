import socket
import json
import requests
from wmf.models import WMFMachineStatConnector

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_address = s.getsockname()[0]
s.close()
data = {}

try:
    with open('ip_address.json') as f:
        data = json.load(f)
except FileNotFoundError:
    wm_conn = WMFMachineStatConnector()
    data = wm_conn.get_wmf_machine_info()
    data['part_number'] = str(wm_conn.part_number)
    with open('ip_address.json', 'w') as f:
        json.dump(data, f)

if data and ip_address.startswith('10.8.'):
    data['ip_internal'] = ip_address
    requests.post('https://wmf24.ru/api/address', json=data)
