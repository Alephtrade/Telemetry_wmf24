from pysnmp.hlapi import *

# Указываем адрес устройства, сообщество и OID
ip_address = '10.8.0.6'
community_string = 'public'
oid = '1.3.6.1.4.1.2021.8'

# Формирование и отправка запроса
errorIndication, errorStatus, errorIndex, varBinds = next(
    getCmd(SnmpEngine(),
           CommunityData(community_string),
           UdpTransportTarget((ip_address, 161)),
           ContextData(),
           ObjectType(ObjectIdentity(oid))
           )
)

# Обработка ответа
if errorIndication:
    print(f'Ошибка: {errorIndication}')
else:
    if errorStatus:
        print(f'Ошибка: {errorStatus}')
    else:
        for varBind in varBinds:
            print(f'{varBind[0]} = {varBind[1]}')