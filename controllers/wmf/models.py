import time
import requests
import websocket
import json
import logging
from controllers.core.utils import print_exception
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.api.beverages import recipes as recipes
from collections import deque
db_conn = WMFSQLDriver()

class WMFMachineErrorConnector:
    WMF_URL = settings.WMF_DATA_URL
    DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS

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
        print(ws)
        print(self.aleph_id)
        try:
            logging.info(f"WMFMachineConnector: message={json.loads(message.encode('utf-8'))}")
            data = WMFMachineStatConnector.normalize_json(message)
            if data.get("function") == 'startPushErrors':
                info = data.get("Info")
                error_code = data.get("ErrorCode")
                if info == "new Error":
                    self.current_errors.add(data.get("ErrorCode"))
                    #last_error_id = db_conn.get_error_last_record()
                    #if last_error_id != [] and last_error_id is not None:
                    #    if last_error_id[0] != "62" and last_error_id[0] != "-1" or last_error_id[1] is not None:
                    self.db_driver.create_error_record(self.aleph_id, error_code)
                    #else:
                elif info == "gone Error":
                    self.db_driver.close_error_code(self.aleph_id, error_code)
                    if error_code in self.current_errors:
                        self.current_errors.remove(error_code)
            if data.get("function") == 'startPushDispensingFinished' or data.get("function") == 'getRecipeComposition':
                print("start")
                print(data.get("RecipeNumber"))
                recipe_number = data.get("RecipeNumber")
                cup_size = data.get("CupSize")
                if cup_size == "CUP_SIZE_Regular":
                    cup_size = "M"
                if cup_size == "CUP_SIZE_Small":
                    cup_size = "S"
                if cup_size == "CUP_SIZE_Large":
                    cup_size = "L"
                recipe_db = self.db_driver.find_machines_recipe_by_id(self.aleph_id, recipe_number)
                print("Recipe")
                print(recipe_number)
                received_data2 = recipes.getRecipeComposition(self.ip, recipe_number)
                #received_data2 = deque(json.loads(received_data))
                print("received_data")
                formatted = {}
                for var in list(deque(json.loads(received_data2))):
                    for i in var:
                        formatted[i] = var[i]
                #if recipe_db and recipe_db is not None:
                columns = {
                    "water": {"count": 0, "weight": 0}, #water
                    "coffee": {"count": 0, "weight": 0}, #coffee
                    "milk": {"count": 0, "weight": 0}, #milk
                    "powder": {"count": 0, "weight": 0}, #powder
                    "foam": {"count": 0, "weight": 0}, #foam
                }
                if data.get("QtyWater") != 0:
                #    columns["water"]["count"] = 1
                    columns["water"]["weight"] = data.get('QtyWater')
                if data.get('QtyGrinder1') != 0 or data.get("QtyGrinder2") != 0 or data.get("QtyGrinder3") != 0 or data.get("QtyGrinder4") != 0:
                #    columns["coffee"]["count"] = 1
                    columns["coffee"]["weight"] = data.get('QtyGrinder1') + data.get('QtyGrinder2') + data.get('QtyGrinder3') + data.get('QtyGrinder4')
                if data.get('QtyMilk1') != 0 or data.get('QtyMilk2') != 0:
                #    columns["milk"]["count"] = 1
                    columns["milk"]["weight"] = data.get('QtyMilk1') + data.get("QtyMilk2")
                if data.get('QtyPowder1') != 0 or data.get('QtyPowder2') != 0:
                #    columns["powder"]["count"] = 1
                    columns["powder"]["weight"] = data.get('QtyPowder1') + data.get('QtyPowder2')
                if data.get('QtyFoam1') != 0 or data.get('QtyFoam2') != 0:
                #    columns["foam"]["count"] = 1
                    columns["foam"]["weight"] = data.get('QtyFoam1') + data.get('QtyFoam2')
                print(0000000000000000000000)
                print(columns)
                receiveddata2 = recipes.getRecipeComposition(self.ip, recipe_number)
                print('composition sended')
                receiveddata2 = deque(json.loads(receiveddata2))
                formatted = {}
                for var in list(receiveddata2):
                    for i in var:
                        formatted[i] = var[i]
                for vat in formatted["Parts"]:
                    print(formatted["Parts"])
                    if vat["Type"] == "coffee":
                        columns["coffee"]["count"] = columns["coffee"]["count"] + 1
                    if vat["Type"] == "coldmilk" or vat["Type"] == "milk":
                        columns["milk"]["weight"] = int(columns["milk"]["weight"] + vat['QtyMilk'])
                        columns["milk"]["count"] = columns["milk"]["count"] + 1
                    if vat["Type"] == "milkfoam" or vat["Type"] == "coldfoam":
                        columns["foam"]["weight"] = int(columns["foam"]["weight"] + vat['QtyFoam'])
                        columns["foam"]["count"] = columns["foam"]["count"] + 1
                    if vat["Type"] == "hotwater" or vat["Type"] == "water":
                        columns["water"]["weight"] = int(columns["water"]["weight"] + vat['QtyWater'])
                        columns["water"]["count"] = columns["water"]["count"] + 1
                columns["coffee"]["weight"] = int(columns["coffee"]["weight"] * columns["coffee"]["count"])
                columns["milk"]["weight"] = int(columns["coffee"]["weight"] * columns["milk"]["count"])  # округлить значение
                columns["foam"]["weight"] = int(columns["coffee"]["weight"] * columns["foam"]["count"])  # округлить значение
                columns["water"]["weight"] = int(columns["coffee"]["weight"] * columns["water"]["count"])  # округлить значение                # округлить значение
                print(22222222222222222222222222)
                print(columns)
            # self.db_driver.save_last_record('current_errors', json.dumps(list(self.current_errors)))
        except Exception as ex:
            logging.error(f"WMFMachineConnector handle_error: error={ex}, stacktrace: {print_exception()}")

    def on_error(self, ws, error):
        logging.info(f"WMFMachineConnector on_error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        requests.post(f'{self.WMF_URL}?device={self.aleph_id}&error_id=0&status=0')
        logging.info(f"WMFMachineConnector on_close: close_status_code = {close_status_code}, close_msg = {close_msg} ")
        ws.send(json.dumps({"function": "stopPushErrors"}))

    def on_open(self, ws):
        print("opened")
        print(self.aleph_id)
        #print(self.aleph_id)
        ws.send(json.dumps({"function": "startPushErrors"}))
        ws.send(json.dumps({"function": "startPushDispensingFinished"}))

    def on_exit(self, ws):
        ws.close()

    def __new__(cls, *args, **kwargs):
        cls.current_errors = set()
        cls.previous_errors = set()
        obj = super().__new__(cls)
        return obj

    def __init__(self, aleph_id, ip):
        try:

            self.aleph_id = aleph_id
            self.ip = ip
            self.db_driver = WMFSQLDriver()
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

    def get_wmf_machine_info(self):
        url = f'{self.WMF_BASE_URL}/api/get-coffee-machine-info/{self.aleph_id}'
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
            self.db_driver = WMFSQLDriver()
            self.current_errors = set()
            self.previous_errors = set()
            self.WS_URL = f'ws://{ip}:{settings.WS_PORT}/'
            self.ws = websocket.create_connection(self.WS_URL, timeout=5)
        except Exception:
            self.ws = None
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
