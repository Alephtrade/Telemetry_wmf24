import requests

WS_IP = '192.168.1.2'
WS_PORT = 25000
WMF_BASE_URL = 'https://backend.wmf24.ru'
WMF_DATA_URL = "https://backend.wmf24.ru/api/errorhook"
WS_URL = f'ws://{WS_IP}:{WS_PORT}/'
DB_PATH = 'controllers/wmf.db'
ERROR_COLLECTOR_INTERVAL_SECONDS = 10
REQUEST_TIMEOUT = 5
DEFAULT_WMF_PARAMS = ''
WEBSOCKET_CONNECT_TIMEOUT = 5
