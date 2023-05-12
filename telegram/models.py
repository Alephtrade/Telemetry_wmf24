import time
import requests
import logging
import random
from os.path import exists
from settings import prod as settings
from core.utils import print_exception


class WMFTelegramBot:

    def __init__(self):
        self.BASE_URL = 'https://api.telegram.org/bot%s/' % settings.TELEGRAM_BOT_TOKEN + '%s'
        self.CHAT_ID = settings.TELEGRAM_CHAT_ID
        self.DEBUGGING_ID = settings.TELEGRAM_DEBUGGING_ID

    def send_message(self, text, debug_mode=False):
        return self._send_request(url=self.BASE_URL % 'sendMessage', data={
            'chat_id': self.DEBUGGING_ID if debug_mode else self.CHAT_ID,
            'text': text
        })

    def send_file(self, file_path, caption='', debug_mode=False):
        if exists(file_path):
            chat_id = self.DEBUGGING_ID if debug_mode else self.CHAT_ID
            url = self.BASE_URL % 'sendDocument?chat_id=' + str(chat_id) + '&caption=' + caption
            return self._send_request(url=url, file_path=file_path)
        return False

    def _send_request(self, url, data=None, file_path=None):
        time.sleep(random.random() * 3)
        for i in range(settings.REQUEST_RETRIES):
            try:
                if data:
                    r = requests.post(url, json=data)
                else:
                    with open(file_path, 'rb') as f:
                        r = requests.post(url, files={
                            'document': f
                        })
                content = r.content.decode('utf-8')
                logging.info(f'WMFTelegramBot _send_request: => {r} {content}')
                if r.status_code == 200:
                    return True
                elif r.status_code == 429:
                    telegram_data = r.json()
                    params = telegram_data.get('parameters')
                    if params:
                        retry_after = params.get('retry_after', 0)
                        if retry_after:
                            time.sleep(retry_after)
                            continue
            except Exception as ex:
                logging.error(f"WMFTelegramBot _send_request: error={ex}, stacktrace: {print_exception()}")
            time.sleep(random.random() * 3)
        return False
