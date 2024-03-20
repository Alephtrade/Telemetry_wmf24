import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
import requests
from pysnmp.hlapi import *
from controllers.db.models import WMFSQLDriver
import json

db_conn = WMFSQLDriver()

def walk(aleph_id, host, oid):
    a = {}
    a["aleph_id"] = aleph_id
    a["modelName"] = ""
    a["serialNum"] = ""
    a["version"] = ""
    a["simCcid"] = ""
    a["signalPower"] = ""
    a["status"] = ""
    a["connectType"] = ""
    i = 1
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                        CommunityData('public'),
                                                                        UdpTransportTarget((host, 161)), ContextData(),
                                                                        ObjectType(ObjectIdentity(oid)),
                                                                        lexicographicMode=False):
        if errorIndication:
            print(errorIndication, file=sys.stderr)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'),
                  file=sys.stderr)
            break
        else:
            for varBind in varBinds:
                a[a.keys()[i]] = varBinds[0][1].prettyPrint()
                i = i + 1
    url = "https://backend.wmf24.ru/api/sim_informer"
    headers = {
        'Content-Type': 'application/json',
        'Serverkey': db_conn.get_encrpt_key()[0]
    }
    #response = requests.request("POST", url, headers=headers, data=json.dumps(a))
    # print(response["aleph_id"])
    return a


devices = db_conn.get_devices()
for device in devices:
    if device[2] is not None and device[2] != "":
        print(walk(device[1], device[2], '1.3.6.1.4.1.2021.8.1.101'))
