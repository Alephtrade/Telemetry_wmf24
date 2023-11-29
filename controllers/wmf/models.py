import requests
import websocket
import json
import logging
from controllers.core.utils import print_exception, get_env_mode, get_part_number_local
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
db_conn = WMFSQLDriver()

class WMFMachineErrorConnector:
    WMF_URL = settings.WMF_DATA_URL
    DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
    ERROR_DESCRIPTION_DICT = {
        13:	'Ошибка мотора, энкодера',
        17:	'Не правильное положение пресса',
        42:	'Аппарат заполняется водой, надо подождать',
        53:	'Требуется очистка',
        55:	'Принудительная промывка, требуется отчистка',
        62:	'Машина выключена, подождать и затем снова включить',
        63:	'Пустой бункер, засыпать зерна',
        64:	'Пустой бункер, засыпать зерна, если есть две кофемолки',
        68:	'Контейнер для кофейной гущи не вставлен, вернуть на место',
        69:	'Контейнер для кофейной гущи заполнен, опорожнить.',
        70:	'Вскоре потребуется опорожнить контейнер для гущи',
        71:	'Счетчик порции достиг максимума, опорожнить контейнер для кофейной гущи',
        72:	'Секция ручной загрузки открыта',
        73:	'Секция ручной загрузки открыта',
        74:	'Панель управления открыта, пожалуйста, закройте панель управления',
        77:	'Обнаружена утечка воды. Выключите и снова включите кофемашину. В случае ошибки позвоните в сервисную службу и закрыть водоснабжение!',
        78:	'Требуется заменить фильтр воды',
        82:	'Залили теплое молоко, или прокисшее',
        83:	'Слишком холодное молоко, либо перемёрзло',
        84:	'Наполнить бак воды',
        87:	'Давление воды во время напитка дозирование слишком низкое. Пожалуйста, откройте воду',
        91:	'Требуется обслуживание варочного блока',
        92:	'Пожалуйста, выполните удаление накипи',
        108:	'Идет разогрев подождите',
        121:	'Идет теплая промывка, подождите',
        123:	'Перезагрузите кофемашину, ошибка варочного блока',
        178:	'Нужно подтвердить, что контейнер для кофейной гущи опорожнен',
        184:	'Идет промывка вспенивателя (форсунки)',
        194:	'Долить молоко',
        213:	'Низкий уровень воды в бойлере, подождать заполнения',
        216:	'Превышен лимит времени заваривания. Перезагрузите кофемашину',
        234:	'Давление в паровом котле слишком низкое. Перезагрузите кофемашину',
        250:	'Низкая температура парового котла, дождаться разогрева',
        255:	'Вставьте варочный блок',
        256:	'Ошибка порционера, перезагрузите кофемашину',
        257:	'Ошибка варочного клапана, перезагрузите кофемашину',
        258:	'Ошибка колебательного насоса, перезагрузите кофемашину',
        259:	'Ошибка выпускного клапана, перезагрузите кофемашину',
        260:	'Ошибка вентилятора, перезагрузите кофемашину',
        261:	'Ошибка клапана подачи горячей воды, перезагрузите кофемашину',
        262:	'Ошибка миксера, перезагрузите кофемашину',
        263:	'Ошибка шоколадного миксера, перезагрузите кофемашину',
        298:	'Перезагрузите кофемашину, ошибка по электричеству',
        299:	'Перезагрузите кофемашину, ошибка по электричеству',
        300:	'Перезагрузите кофемашину, ошибка по электричеству',
        301:	'Перезагрузите кофемашину, ошибка по электричеству',
        302:	'Перезагрузите кофемашину, ошибка по электричеству',
        303:	'Перезагрузите кофемашину, ошибка по электричеству',
        304:	'Перезагрузите кофемашину, ошибка по электричеству',
        305:	'Перезагрузите кофемашину, ошибка по электричеству',
        306:	'Перезагрузите кофемашину, ошибка по электричеству',
        307:	'Перезагрузите кофемашину, ошибка по электричеству',
        335:	'Ошибка по датчику перегрева пара, перезагрузите кофемашину',
        336:	'Ошибка по датчику отпаривателя с температурным датчиком',
        344:	'Уровень молока на нуле, долить молоко',
        345:	'Уровень молока на нуле, долить молоко',
        346:	'Пожалуйста долейте молоко',
        347:	'Высокая температура молочной системы, проверьте молоко',
        357:	'Нет давления в водоснабжении',
        358:	'Молоко в холодильнике слишком теплое',
        361:	'Требуется отчистка молочной системы',
        364:	'Датчик каплеуловителя грязный, либо опорожнить каплеуловитель. Очистка каплеуловителя',
        368:	'Ошибка по счетчику воды (флоуметр), требуется перезагрузка',
        370:	'Эко режим',
        398:	'Дверца шоколадного миксера открыта',
        400:	'Ошибка конфигураций, перезагрузите кофемашину',
        406:	'Ошибка входе перезагрузки, перезагрузите кофемашину',
        429:	'Проверить правильность положения Варочного блока',
        452:	'Ошибка по току, редуктор варочного, перезагрузите кофемашину',
        453:	'Ошибка по току, редуктор варочного, перезагрузите кофемашину',
        454:	'Ошибка по току, перезагрузите кофемашину',
        455:	'Ошибка по току, перезагрузите кофемашину',
        456:	'Ошибка по варочному блоку, перезагрузите кофемашину',
        457:	'Ошибка по кофемолке, перезагрузите кофемашину',
        458:	'Ошибка шоколадного миксера, перезагрузите кофемашину',
        459:	'Ошибка шоколадного миксера, перезагрузите кофемашину',
        463:	'Ошибка защиты, перезагрузите кофемашину',
        467:	'Пополнить контейнер для кофе',
        468:	'Пополнить контейнер для кофе (если есть вторая кофемолка)',
        469:	'Мало кофе в варочной камере',
        470:	'Мало кофе в варочной камере',
        475:	'Вставить каплеуловитель на место',
        476:	'Вставить на место контейнер для кофейной гущи',
        477:	'Обнаружен сбой питания. Перезагрузите кофемашину',
        478:	'Высокая мощность потребления. Перезагрузите кофемашину',
        479:	'Ошибка по току, звоните в сервис',
        480:	'Ошибка по току, звоните в сервис',
        484:	'Ошибка по воде. Проверить воду в баке, в насосе, в центральном водоснабжении',
        485:	'Ошибка по пережимному клапану',
        486:	'Ошибка по пережимному клапану',
        487:	'Варочный блок не правильно вставлен. Проверить правильность',
        488:	'Секция ручной загрузки открыта слишком долго. Закрыть секцию ручной загрузки',
        489:	'Закройте ручную секцию для загрузки таблетки',
        490:	'Ошибка по варочному блоку, перезагрузите кофемашину',
        491:	'Идет промывка миксера',
        492:	'Срок сервисного обслуживания. Звоните в сервис',
        493:	'Срок сервисного обслуживания. Звоните в сервис',
        494:	'Срок сервисного обслуживания. Звоните в сервис',
        495:	'Срок сервисного обслуживания. Звоните в сервис',
        496:	'Срок сервисного обслуживания. Звоните в сервис',
        497:	'Срок сервисного обслуживания. Звоните в сервис',
        498:	'Срок сервисного обслуживания. Звоните в сервис',
        499:	'Срок сервисного обслуживания. Звоните в сервис',
        500:	'Срок сервисного обслуживания. Звоните в сервис',
        501:	'Срок сервисного обслуживания. Звоните в сервис',
        502:	'Запущена очистка молочной системы',
        505:	'Ошибка редуктора варочного блока, перезагрузить кофемашину',
        506:	'Требуется завершить очистку молока',
        507:	'Требуется очистить варочный блок вручную',
        508:	'Ошибка датчика температуры. Перезагрузить кофемашину, звонить в сервис',
        509:	'Ошибка датчика температуры. Перезагрузить кофемашину, звонить в сервис',
        510:	'Молоко теплое возможно отключен холодильник',
        511:	'Пожалуйста, продолжите и завершите удаление накипи',
        512:	'Обрыв датчика температуры, перезагрузите кофемашину, звоните в сервис',
        513:	'Ошибка флоуметра, перезагрузите кофемашину, звоните в сервис',
        514:	'Датчик для кофейной гущи не на месте',
        516:	'Кофемолка номер 1 заблокирована, звоните в сервис',
        517:	'Кофемолка номер 2 заблокирована, звоните в сервис',
        518:	'Кофемолка номер 3 заблокирована, звоните в сервис',
        519:	'Кофемолка номер 4 заблокирована, звоните в сервис',
        527:	'Ошибка по редуктору кофемолки. Звоните в сервис',
        528:	'Заканчивается промывка, подождите',
        529:	'Ручная секция для загрузки, открыта. Закройте',
        530:	'Принудительная промывка молочной системы',
        531:	'Машина отключается.',
        532:	'Варочный блок не правильно вставлен. Проверить правильность',
        534:	'Подождите идет запуск машины',
        535:	'Заполнение бойлера ждите',
        539:	'Заполните молочный бункер',
        540:	'Разогрев',
        572:	'Опорожнить каплеуловитель',
        574:	'Машинка была отключена не правильно. Вытащить из розетки, затем снова включить',
        582:	'Очистка прервана, перезагрузите кофемашину',
        583:	'Ошибка бойлера, перезагрузите',
        584:	'Требуется удаление накипи',
        587:	'Промыть каплеуловитель и вставить на место',
        588:	'Проверить водяной бак, прочистить сенсор',
        589:	'Ошибка по воде, проверьте подачу воды',
        590:	'Вернуть бак воды на место.',
        591:	'Датчик каплеуловителя грязный, либо опорожнить каплеуловитель. Очистка каплеуловителя',
        592:	'Проверить водяной бак, прочистить сенсор.',
        593:	'Во время варки, заполнился каплеуловитель, опорожнить',
        594:	'Бак для воды наполнятся, подождите',
        595:	'Внешний бак для сточных вод полный',
        596:	'Блок питания отключен, перезагрузите кофемашину',
        600:	'Закрыть брызговик',
        604:	'Варка прервана, закончилась вода, заполнить бак и продолжить пролив напитка',
        605:	'Забрать напиток',
        608:	'Теплое ополаскивание кофемашины',
        609:	'Температура кофемашины нарушена, перезагрузите',
        610:	'Проводится калибровка насоса, подождите',
        614:	'Долейте молоко',
        617:	'Долейте молоко',
        618:	'Долейте молоко',
        630:	'Машина разогревается после ECO режима, подождите',
        631:	'Продолжается выдача напитков, подождите',
        632:	'Не удалось загрузить базу данных, перезагрузите кофемашину',
        633:	'Не удалось загрузить базу данных, перезагрузите кофемашину',
        634:	'Не удалось загрузить базу данных, перезагрузите кофемашину',
        635:	'Не удалось загрузить базу данных, перезагрузите кофемашину',
        638:	'Не удалось загрузить базу данных, перезагрузите кофемашину',
        639:	'Не удалось загрузить базу данных, перезагрузите кофемашину',
        640:	'Идет наполнение бака, подождите.',
        641:	'Заполнение бойлера ждите',
        662:	'Заменить фильтр воды',
        664:	'Очистка прервана, проведите еще раз',
        827:	'Идет/требуется обновление прошивки',
        852:	'SD карта не обнаружена',
        879:	'Не найдены рецепты, загрузите рецепты',
        880:	'Не верный настройки текущего времени',
        881:	'Кофе готовка с молотым кофе. Перезагрузить машинку',
        883:	'Версия прошивки несовместима, установите верную прошивку',
        884:	'Версия прошивки несовместима, установите верную прошивку',
        885:	'Версия прошивки несовместима, установите верную прошивку',
        887:	'Версия прошивки несовместима, установите верную прошивку',
        890:	'Версия прошивки несовместима, установите верную прошивку',
        'F120':	'Ошибка по току',
        'F121':	'Ошибка CAN кабеля',
        'F130':	'Ошибка по току',
        'F149':	'Ошибка по току',
        'F161':	'Забит варочный блок',
        'F162':	'Забит варочный блок',
        'F164':	'Возможно кончилась вода при варки кофе. Проверить',
        'F165':	'Ошибка по току',
        'F167':	'Ошибка по току',
        'F185':	'Ошибка по току',
        'F186':	'Ошибка по току',
        'F187':	'Ошибка сенсора',
        'F188':	'Ошибка бойлера, звоните в сервис',
        'F189':	'Ошибка бойлера, звоните в сервис',
        'F2':	'Ошибка по току',
        'F3':	'Ошибка по току',
        'F6':	'Ошибка по току',
        'F7':	'Варочный блок удален, поставить назад',
        'F87':	'Ошибка по току',
        'F88':	'Ошибка по току',
        'F89':	'Ошибка по току'
    }

    def get_part_number(self):
        try:
            ws = websocket.create_connection(self.WS_URL)
            request = json.dumps({'function': 'getMachineInfo'})
            logging.info(f"COFFEE_MACHINE: Sending {request}")
            ws.send(request)
            received_data = ws.recv()
            logging.info(f"COFFEE_MACHINE: Received {received_data}")
            ws.close()
            return WMFMachineStatConnector.normalize_json(received_data).get('PartNumber')
        except Exception as ex:
            logging.info(f"COFFEE_MACHINE: Get machine info error, HOST {self.WS_URL} - {ex}")
            print(ex)
            return None

    def get_status(self):
        try:
            ws = websocket.create_connection(self.WS_URL, timeout=settings.WEBSOCKET_CONNECT_TIMEOUT)
            if ws.connected:
                ws.close()
                return 1
        except Exception:
            return 0

    def on_message(self, ws, message):
        print(message)
        try:
            logging.info(f"WMFMachineConnector: message={json.loads(message.encode('utf-8'))}")
            data = WMFMachineStatConnector.normalize_json(message)
            if data.get("function") == 'startPushErrors':
                info = data.get("Info")
                error_code = data.get("ErrorCode")
                error_text = self.ERROR_DESCRIPTION_DICT.get(error_code) or data.get("Error Text")
                if info == "new Error":
                    self.current_errors.add(data.get("ErrorCode"))
                    #last_error_id = db_conn.get_error_last_record()
                    #if last_error_id != [] and last_error_id is not None:
                    #    if last_error_id[0] != "62" and last_error_id[0] != "-1" or last_error_id[1] is not None:
                    self.db_driver.create_error_record(self.aleph_id, error_code, error_text)
                    #else:
                    #    self.db_driver.create_error_record(error_code, error_text)
                elif info == "gone Error":
                    self.db_driver.close_error_code(self.aleph_id, "74")
                    if error_code in self.current_errors:
                        self.current_errors.remove(error_code)
            if data.get("function") == 'startPushDispensingFinished':
                info = data
                logging.info(f"WMFMachineConnector: message={data}")
            # self.db_driver.save_last_record('current_errors', json.dumps(list(self.current_errors)))
        except Exception as ex:
            logging.error(f"WMFMachineConnector handle_error: error={ex}, stacktrace: {print_exception()}")

    def on_error(self, ws, error):
        logging.info(f"WMFMachineConnector on_error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        requests.post(f'{self.WMF_URL}?code={self.part_number}&{self.DEFAULT_WMF_PARAMS}&error_id=0&status=0')
        logging.info(f"WMFMachineConnector on_close: close_status_code = {close_status_code}, close_msg = {close_msg} ")
        ws.send(json.dumps({"function": "stopPushErrors"}))

    def on_open(self, ws):
        print("opened")
        ws.send(json.dumps({"function": "startPushErrors"}))
        ws.send(json.dumps({"function": "startPushDispensingFinished"}))

    def on_exit(self, ws):
        ws.close()

    def __init__(self, aleph_id, ip):
        try:
            self.aleph_id = aleph_id
            self.part_number = get_part_number_local()
            self.db_driver = WMFSQLDriver()
            self.current_errors = set()
            self.previous_errors = set()
            self.WS_URL = f'ws://{ip}:{settings.WS_PORT}/'
            self.ws = websocket.WebSocketApp(self.WS_URL,
                                             on_open=self.on_open,
                                             on_message=self.on_message,
                                             on_error=self.on_error,
                                             on_close=self.on_close)
        except Exception as ex:
            logging.error(f"WMFMachineConnector init: error={ex}, stacktrace: {print_exception()}")

    def run_websocket(self):
        websocket.enableTrace(False)
        self.ws.run_forever()

    def close(self):
        self.ws.close()
        self.db_driver.close()


class WMFMachineStatConnector:
    WS_URL = settings.WS_URL
    WMF_BASE_URL = settings.WMF_BASE_URL

    def get_part_number(self):
        try:
            data = self.send_wmf_request('getMachineInfo')
            part_number = data.get('PartNumber')
            #with open('/root/wmf_1100_1500_5000_router/part_number.txt', 'w') as f:
            #    f.write(str(part_number))
            return part_number
        except Exception:
         #   with open('/root/wmf_1100_1500_5000_router/part_number.txt') as f:
            return Exception

    def get_wmf_machine_info(self):
        url = f'{self.WMF_BASE_URL}/api/get-coffee-machine-info/{self.part_number}'
        logging.info(f"WMFMachineStatConnector: GET {url}")
        r = requests.get(url)
        logging.info(f"WMFMachineStatConnector: GET response: {r.content.decode('utf-8')}")
        data = r.json()
        with open('/root/wmf_1100_1500_5000_router/machine_info.txt', 'w') as f:
            f.write('Компания {company}, Филиал {filial}'.format(**data))
        return data

    def get_beverages_count(self):
        if self.ws:
            data = self.send_wmf_request('getBeverageStatistics')
            self.beverage_stats_raw = data
            result = 0
            print(data)
            for k, v in data.items():
                if k not in ('function', 'returnvalue'):
                    result += int(v) if v else 0
            return result
        else:
            return None

    def get_system_cleaning_state(self):
        if self.ws:
            data = self.send_wmf_request('getSystemCleaningState')
            return data
        else:
            return None

    def get_milk_cleaning_state(self):
        if self.ws:
            data = self.send_wmf_request('getMilkCleaningState')
            return data
        else:
            return None

    def get_foamer_rinsing_state(self):
        if self.ws:
            data = self.send_wmf_request('getFoamerRinsingState')
            return data
        else:
            return None

    def get_milk_replacement_state(self):
        if self.ws:
            data = self.send_wmf_request('getMilkReplacementState')
            return data
        else:
            return None

    def get_mixer_rinsing_state(self):
        if self.ws:
            data = self.send_wmf_request('getMixerRinsingState')
            return data
        else:
            return None

    def get_milk_mixer_warm_rinsing_state(self):
        if self.ws:
            data = self.send_wmf_request('getMilkMixerWarmRinsingState')
            return data
        else:
            return None

    def get_ffc_filter_replacement_state(self):
        if self.ws:
            data = self.send_wmf_request('getFfcFilterReplacementState')
            return data
        else:
            return None

    def get_cleaning_duration(self):
        if self.ws:
            return self.send_wmf_request('getSystemCleaningState')['durationInSeconds']
        return None

    def get_error_active_count(self):
        if self.ws:
            return self.send_wmf_request('getErrorActiveCount')
        return None

    def get_error_active(self):
        if self.ws:
            request = json.dumps({"function":"getErrorActive","a_iIndex":0})
            logging.info(f"COFFEE_MACHINE: Sending {request}")
            self.ws.send(request)
            received_data = self.ws.recv()
            return received_data
        return None

    def get_cleaning_state(self):
        if self.ws:
            data = self.send_wmf_request('getSystemCleaningState')
            if data['returnvalue'] == 0:
                if data['durationInSeconds'] == -1:
                    return 'промывка не производилась❌'
                else:
                    return 'промывка производилась✅'
            else:
                return 'информацию не удалось получить❗'
        else:
            return None

    def __init__(self, aleph_id, ip):
        try:
            self.aleph_id = aleph_id
            self.part_number = get_part_number_local()
            self.db_driver = WMFSQLDriver()
            self.current_errors = set()
            self.previous_errors = set()
            self.WS_URL = f'ws://{ip}:{settings.WS_PORT}/'
            self.ws = websocket.create_connection(self.WS_URL, timeout=5)
        except Exception:
            self.ws = None
        self.part_number = self.get_part_number()
        self.beverage_stats_raw = None

    def close(self):
        if self.ws:
            self.ws.close()

    @staticmethod
    def normalize_json(data):
        return json.loads(data.replace('{', '').replace('}', '').replace('[', '{').replace(']', '}'))

    def send_wmf_request(self, wmf_command):
        request = json.dumps({'function': wmf_command})
        logging.info(f"WMFMachineStatConnector: Sending {request}")
        self.ws.send(request)
        received_data = self.ws.recv()
        logging.info(f"WMFMachineStatConnector: Received {received_data}")
        return self.normalize_json(received_data)
