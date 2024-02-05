import websocket
import logging
import requests
import socket
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.core.utils import timedelta_int, get_beverages_send_time, initialize_logger
from controllers.api.beverages import methods
from controllers.wmf.models import WMFMachineStatConnector
db_conn = WMFSQLDriver()


def handle_client(client_socket):
    # Получение данных от клиента
    data = client_socket.recv(1024)
    if data:
        # Вывод сообщения
        print(data.decode())


devices = db_conn.get_devices()
for device in devices:
    db_driver = WMFSQLDriver()
    WS_URL = f'ws://{device[2]}:25000/'

    status = None
    try:
        ws = websocket.create_connection(WS_URL, timeout=settings.WEBSOCKET_CONNECT_TIMEOUT)
        if ws.connected:
            ws.close()
            status = 1
            sockets = []
            for i in range(3):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((device[2], 25000 + i))
                sock.listen(1)
                sockets.append(sock)
                while True:
                    for sock in sockets:
                        client_socket, addr = sock.accept()
                        handle_client(client_socket)

    except Exception:
        status = 0,
        print("status: 0")


