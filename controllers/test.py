import sys

from pysnmp.hlapi import *


def walk(host, oid):
    a = []
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
                a[varBinds[0][0].prettyPrint()] = varBinds[0][1].prettyPrint()
    return a


print(walk('10.8.0.6', '1.3.6.1.4.1.2021.8.1.101'))
