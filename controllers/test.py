import websocket
import logging
import requests
import threading
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

devices = db_conn.get_devices()
for device in devices:
    db_driver = WMFSQLDriver()
    WS_URL = f'ws://{device[2]}:25000/'
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((device[2], 25000))
    server.listen(15)
    print(f'Server{device[2]} 25000 start.')

users = []  # To store their name
sort = []  # To store their socket


def listen_user(user):
    print('Listening user')
    sort.append(user)  # Store their socket in sort[]
    user.send('Name'.encode('utf-8'))  # send 'Name' to clients
    name = user.recv(1024).decode('utf-8')  # Receive their name
    users.append(name)  # Store their name in user[]

    while True:
        data = user.recv(1024).decode('utf-8')
        print(f'{name} sent {data}')

        for i in sort:  # Send received messages to clients
            if (i != server and i != user):  # Filter server and message sender. Send message except them.
                i.sendall(f'{name} > {data}'.encode('utf-8'))


def start_server():
    while True:
        user_socket, addr = server.accept()
        potok_info = threading.Thread(target=listen_user, args=(user_socket,))
        potok_info.start()


if __name__ == '__main__':
    start_server()


