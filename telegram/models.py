import time
import requests
from settings import prod as settings


class WMFTelegramBot:

    def __init__(self):
        self.BASE_URL = 'https://api.telegram.org/bot%s/' % settings.TELEGRAM_BOT_TOKEN + '%s'
        self.CHAT_ID = settings.TELEGRAM_CHAT_ID
        self.DEBUGGING_ID = settings.TELEGRAM_DEBUGGING_ID

    def send_message(self, text, debug_mode=False):
        chat_id = self.CHAT_ID
        if debug_mode:
            chat_id = self.DEBUGGING_ID
        d = {
            'chat_id': chat_id,
            'text': text
        }
        return self._send_request(url=self.BASE_URL % 'sendMessage', data=d)

    def send_file(self, file_path, caption='', debug_mode=False):
        with open(file_path, 'rb') as f:
            files = {
                'document': f
            }
            chat_id = self.CHAT_ID
            if debug_mode:
                chat_id = self.DEBUGGING_ID
            url = self.BASE_URL % 'sendDocument?chat_id=' + str(chat_id) + '&caption=' + caption
            self._send_request(url=url, files=files)

    def _send_request(self, url, data=None, files=None):
        for i in range(settings.REQUEST_RETRIES):
            try:
                r = requests.post(url, json=data, files=files)
                if r.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(1)
        return False
