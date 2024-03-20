from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget,\
                         ContextData, ObjectType, ObjectIdentity, getCmd

iterator = getCmd(
    SnmpEngine(),
    CommunityData('public', mpModel=1),
    UdpTransportTarget(('10.8.0.6', 161)),
    ContextData(),
    ObjectType(ObjectIdentity('1.3.6.1.4.1.2021.8.1.101'))
)

errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

if errorIndication:
    print(errorIndication)
elif errorStatus:
    print('{} at {}'.format(errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

for oid, val in varBinds:
    print(f'{oid.prettyPrint()} = {val.prettyPrint()}')