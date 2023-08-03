import requests


WS_IP = '192.168.8.101'
WS_PORT = 25000
WMF_BASE_URL = 'https://wmf24.ru'
WMF_DATA_URL = "https://wmf24.ru/api/errorhook"
WS_URL = f'ws://{WS_IP}:{WS_PORT}/'
DB_PATH = '/root/wmf_1100_1500_5000_router/wmf.db'
TELEGRAM_BOT_TOKEN = '5797272389:AAFF7214btV4YpA0GgCQDmuRfi-zff2EtIM'
TELEGRAM_CHAT_ID = ''
TELEGRAM_DEBUGGING_ID = '-1001516057504'
ERROR_COLLECTOR_INTERVAL_SECONDS = 5
CHECK_MACHINE_STATUS_INTERNAL = 1 * 60
REQUEST_TIMEOUT = 5
DEFAULT_WMF_PARAMS = 'cocoa=99&coffee=99&milk=99&water=99&draining=0'
LOGGER_TEXT_LIMIT = 512
WEBSOCKET_CONNECT_TIMEOUT = 5
TELEGRAM_REPORT_INTERVAL_MINUTES = 24 * 60
TELEGRAM_REPORT_RECORDS_TO_KEEP = 30
CLEAN_DB_DAYS = 30
REQUEST_RETRIES = 5


def get_chat_id():
    if TELEGRAM_CHAT_ID == '' :
        try:
            with open('/root/wmf_1100_1500_5000_router/part_number.txt') as f:
                part_number = f.read()
        except Exception:
            return ''
        #print(part_number)
        url = f'{WMF_BASE_URL}/api/get-coffee-machine-info/{part_number}'
        #print(url)
        r = requests.get(url)
        #print(r)
        data = r.json()
        #print(data)
        s = data["telegram_chat_id"]
        return TELEGRAM_CHAT_ID


print(get_chat_id())
