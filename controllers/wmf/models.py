import time
import requests
import websocket
import json
import logging
from datetime import timedelta, datetime, time
from controllers.core.utils import print_exception
from controllers.db.models import WMFSQLDriver
from controllers.settings import prod as settings
from controllers.api.beverages import recipes as recipes
from collections import deque
from controllers.api.beverages import Drinks as DrinksManager
db_conn = WMFSQLDriver()

class WMFMachineErrorConnector:
    WMF_URL = settings.WMF_DATA_URL
    DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS

    def get_status(self):
        try:
            ws = websocket.create_connection(f'ws://{self.ip}:25000/', timeout=5)
            if ws.connected:
                ws.close()
                return 1
        except Exception:
            return 0

    def handler_of_active_errors(self, ws):
            received_error = ws.recv()
            # return print(received_drinks)
            received_error_deque = deque(json.loads(received_error))
            formatted_error = {}
            for var_error in list(received_error_deque):
                for i_error in var_error:
                    formatted_error[i_error] = var_error[i_error]
            if formatted_error["ulErrorCode"] != 0:
                actual_finder = db_conn.get_unclosed_error_by_code(formatted_error["ulErrorCode"], self.aleph_id)
                if actual_finder is None:
                    db_conn.create_error_record(self.aleph_id, formatted_error["ulErrorCode"])



    def on_message(self, ws, message):
        #print(message)
        #print(ws)
        #print(self.aleph_id)
        try:
            #logging.info(f"WMFMachineConnector: message={json.loads(message.encode('utf-8'))}")
            data = WMFMachineStatConnector.normalize_json(message)
            #print(data.get("function"))
            if data.get("function") == 'startPushDispensingStarted':
                status = db_conn.get_machine_block_status(self.aleph_id)[0][0]
                #print(status)
                if status == "1":
                    message = ws.send(json.dumps({"function": "reboot"}))
                    print(message)
            if data.get("function") == 'getErrorActive':
                #print('getErrorActive')
                #print("ulErrorCode")
                #print(data.get("ulErrorCode"))
                if data.get("ulErrorCode") != 0:
                    actual_finder = db_conn.get_unclosed_error_by_code(data.get("ulErrorCode"), self.aleph_id)
                    print(actual_finder)
                    if actual_finder is None:
                        db_conn.create_error_record(self.aleph_id, data.get("ulErrorCode"))
                        self.index_active_error += 1
                        ws.send(json.dumps({"function": "getErrorActive", "a_iIndex": self.index_active_error}))
                        #print("+1")
                else:
                    self.last_error_code_in_index = -1
                    #print("-1")
            if data.get("function") == 'startPushErrors':
                info = data.get("Info")
                error_code = data.get("ErrorCode")
                if info == "new Error":
                    self.current_errors.add(data.get("ErrorCode"))
                    print("New Error")
                    #last_error_id = db_conn.get_error_last_record()
                    #if last_error_id != [] and last_error_id is not None:
                    #    if last_error_id[0] != "62" and last_error_id[0] != "-1" or last_error_id[1] is not None:
                    self.db_driver.create_error_record(self.aleph_id, error_code)
                    if(error_code == "62"):
                        self.db_driver.create_error_record(self.aleph_id, '-1')
                        self.db_driver.close_error_code(self.aleph_id, "62")
                        last_sixtwo = self.db_driver.get_error_last_stat_record("62", self.aleph_id)
                        request = f'{self.WMF_URL}?device={self.aleph_id}&error_id=62&date_start={last_sixtwo[2]}&date_end={datetime.fromtimestamp(int(datetime.now().timestamp()))}&duration={last_sixtwo[3]}&status={self.get_status()}'

                    #else:
                elif info == "gone Error":
                    self.db_driver.close_error_code(self.aleph_id, error_code)
                    if error_code in self.current_errors:
                        self.current_errors.remove(error_code)
            if data.get("function") == 'startPushDispensingFinished' or data.get("function") == 'getRecipeComposition':
                #print(data)
                #print(data.get("RecipeNumber"))
                recipe_number = data.get("RecipeNumber")
                cup_size = data.get("CupSize")
                if cup_size == "CUP_SIZE_Regular" or cup_size == "Regular":
                    cup_size = "M"
                if cup_size == "CUP_SIZE_Small" or cup_size == "Small":
                    cup_size = "S"
                if cup_size == "CUP_SIZE_Large" or cup_size == "Large":
                    cup_size = "L"
                #print("Recipe")
                #print(recipe_number)
                self.available_recipe = db_conn.getRecipe(self.aleph_id, recipe_number)
                if self.available_recipe is None or self.available_recipe:
                    #print("UPDATER")
                    print(self.ip)
                    #self.drink_list = DrinksManager.updateDrinks(self.ip)
                if self.available_recipe is not None and self.available_recipe:
                    water = 0
                    coffee = 0
                    milk = 0
                    powder = 0
                    foam = 0
                    if cup_size == "S" or cup_size == "L":
                        water = int(self.available_recipe[7]) * int(data.get("QtyWater"))
                        coffee = int(self.available_recipe[5]) * (int(data.get("QtyGrinder1")) + int(data.get("QtyGrinder2")) + int(data.get("QtyGrinder3")) + int(data.get("QtyGrinder4")))
                        milk = int(self.available_recipe[9]) * (int(data.get("QtyMilk1")) + int(data.get("QtyMilk2")))
                        powder = int(self.available_recipe[11]) * (int(data.get("QtyPowder1")) + int(data.get("QtyPowder2")))
                        foam = int(self.available_recipe[13]) * (int(data.get("QtyFoam1")) + int(data.get("QtyFoam2")))
                    elif cup_size == "M":
                        water = self.available_recipe[8]
                        coffee = self.available_recipe[6]
                        milk = self.available_recipe[10]
                        powder = self.available_recipe[12]
                        foam = self.available_recipe[14]
                    #print(self.aleph_id)
                    #print("self.aleph_id")
                    date_formed = datetime.fromtimestamp(int((datetime.now()).timestamp()))
                    booler = db_conn.if_pours_created(self.aleph_id, date_formed)
                    #print({self.aleph_id, date_formed})
                    #print(booler)
                    if booler is None:
                        db_conn.initPours(self.aleph_id, recipe_number, self.available_recipe[3], cup_size, water, coffee, milk, powder, foam, date_formed)
            sorter = []
            not_sort_pours = db_conn.get_all_pours_not_sended(self.aleph_id)
            #print("not_sort_pours")
            #print(not_sort_pours)
            for key in not_sort_pours:
             #   print(key)
                time_check = datetime.fromtimestamp(datetime.strptime(key[10], '%Y-%m-%d %H:%M:%S').timestamp() // (60 * 60) * 60 * 60)
              #  print(datetime.fromtimestamp(int(datetime.now().timestamp())))
              #  print(time_check)
                if datetime.fromtimestamp(int(datetime.now().timestamp())) > time_check:
                #print("time now")
                    device_utc = db_conn.get_device_field_by_aleph_id(key[1], "utc")[0]
                    sorter.append({"id": key[0], "aleph_id": key[1], "recipe_id": key[2], "recipe_name": key[3],
                                   "cup_size": key[4], "water": key[5], "coffee": key[6], "milk": key[7],
                                   "powder": key[8], "foam": key[9],
                                   "date_formed": (time_check + timedelta(seconds=int(device_utc)) + timedelta(seconds=3599)).strftime('%Y-%m-%d %H:%M:%S')})
            #print("sorter")
            #print(sorter)
            url = "https://backend.wmf24.ru/api/new_pour"
            headers = {
                'Content-Type': 'application/json',
                'Serverkey': db_conn.get_encrpt_key()[0]
            }
            response = requests.request("POST", url, headers=headers, data=json.dumps(sorter))
            #print(response)
            if response.status_code == 200:
                # print(sorter)
                for pour in sorter:
                    # print(pour)
                    #print(pour["id"])
                    db_conn.id_pours_sended(pour["id"])
                    #data_to_send = {}
                    #data_to_send["aleph_id"] = self.aleph_id
                    #data_to_send["recipe_id"] = recipe_number
                    #data_to_send["recipe_name"] = available_recipe[3]
                    #data_to_send["cup_size"] = cup_size
                    #data_to_send["water"] = water
                    #data_to_send["coffee"] = coffee
                    #data_to_send["milk"] = milk
                    #data_to_send["powder"] = powder
                    #data_to_send["foam"] = foam
                    #url = "https://backend.wmf24.ru/api/new_pour"
#
                    #headers = {
                    #    'Content-Type': 'application/json',
                    #    'Serverkey': db_conn.get_encrpt_key()[0]
                    #}
                    #response = requests.request("POST", url, headers=headers, data=json.dumps(data_to_send))
                    #logging.error(f"WMFMachineConnector handle_error: pour={response}, stacktrace: {print_exception()}")

            # self.d    b_driver.save_last_record('current_errors', json.dumps(list(self.current_errors)))
        except Exception as ex:
            print("error")
            #logging.error(f"WMFMachineConnector handle_error: error={ex}, stacktrace: {print_exception()}")

    def on_error(self, ws, error):
        print(error)
        #logging.info(f"WMFMachineConnector on_error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        requests.post(f'{self.WMF_URL}?device={self.aleph_id}&error_id=0&status=0')
        #logging.info(f"WMFMachineConnector on_close: close_status_code = {close_status_code}, close_msg = {close_msg} ")
        ws.send(json.dumps({"function": "stopPushErrors"}))
        ws.send(json.dumps({"function": "stopPushDispensingFinished"}))

    def on_open(self, ws):
        print("opened")
        print(self.aleph_id)
        #print(self.last_error_code_in_index)
        ws.send(json.dumps({"function": "getErrorActive", "a_iIndex": self.index_active_error}))
        ws.send(json.dumps({"function": "startPushErrors"}))
        ws.send(json.dumps({"function": "startPushDispensingFinished"}))
        ws.send(json.dumps({"function": "startPushDispensingStarted"}))


    def on_exit(self, ws):
        ws.close()

    def __new__(cls, *args, **kwargs):
        cls.current_errors = set()
        cls.drink_list = set()
        cls.previous_errors = set()
        obj = super().__new__(cls)
        return obj

    def __init__(self, aleph_id, ip):
        try:
            self.aleph_id = aleph_id
            self.ip = ip
            self.index_active_error = 0
            self.last_error_code_in_index = 0
            self.available_recipe = ""
            self.db_driver = WMFSQLDriver()
            self.WS_URL = f'ws://{ip}:{settings.WS_PORT}/'
            self.ws = websocket.WebSocketApp(self.WS_URL,
                                             on_open=self.on_open,
                                             on_message=self.on_message,
                                             on_error=self.on_error,
                                             on_close=self.on_close)
        except Exception as ex:
            print("error")
            #logging.error(f"WMFMachineConnector init: error={ex}, stacktrace: {print_exception()}")

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
        #logging.info(f"WMFMachineStatConnector: GET {url}")
        r = requests.get(url)
        #logging.info(f"WMFMachineStatConnector: GET response: {r.content.decode('utf-8')}")
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
            #logging.info(f"COFFEE_MACHINE: Sending {request}")
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
        #logging.info(f"WMFMachineStatConnector: Sending {request}")
        self.ws.send(request)
        received_data = self.ws.recv()
        #logging.info(f"WMFMachineStatConnector: Received {received_data}")
        return self.normalize_json(received_data)
