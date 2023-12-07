import requests

WS_IP = '192.168.1.2'
WS_PORT = 25000
WMF_BASE_URL = 'https://backend.wmf24.ru'
WMF_DATA_URL = "https://backend.wmf24.ru/api/errorhook"
WS_URL = f'ws://{WS_IP}:{WS_PORT}/'
DB_PATH = '/var/www/Telemetry_wmf24/controllers/wmf.db'
ERROR_COLLECTOR_INTERVAL_SECONDS = 5
REQUEST_TIMEOUT = 5
DEFAULT_WMF_PARAMS = 'cocoa=99&coffee=99&milk=99&water=99&draining=0'
WEBSOCKET_CONNECT_TIMEOUT = 5
