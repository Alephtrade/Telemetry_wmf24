import json
import logging
import websocket
import ast
from datetime import datetime, timedelta
import sys
import requests
import re
sys.path.append("../../")
from controllers.db.models import WMFSQLDriver
from controllers.core.utils import initialize_logger, get_beverages_send_time
from controllers.settings import prod as settings
from controllers.wmf.models import WMFMachineStatConnector

WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()
WMF_URL = settings.WMF_DATA_URL


def Take_Create_Beverage_Statistics(last_send, device):
    print(device)
    initialize_logger('beveragestatistics.log')
    wm_conn = WMFMachineStatConnector(device[1], device[2])
    fake_data = False
    summ = 0
    device_code = ""
    recipes = []
    date_to_send = get_beverages_send_time(last_send)
    next_time = datetime.strptime(str(date_to_send), '%Y-%m-%d %H:%M:%S')
    #date_to_send = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    date_formed = datetime.fromtimestamp(int(datetime.now().timestamp() // (60 * 60) * 60 * 60) - 1)
    try:
        WS_IP = f'ws://{device[2]}:25000/'
        ws = websocket.create_connection(WS_IP, timeout=5)
        fake_data = False
    except Exception:
        ws = None
        fake_data = True
        logging.info(f"error {wm_conn.ws}")
    if not wm_conn.ws:
        logging.info(f"error {wm_conn.ws}")
        fake_data = True
    else:
        request = json.dumps({'function': 'getBeverageStatistics'})
        ws.send(request)
        received_data = ws.recv()
        logging.info(f"{received_data}")
        if received_data is not None or received_data != []:
            received_data = received_data.replace(']', '', 1)
            received_data = received_data + ', {"device" : ' + '"' + device[1] + '"' + '}]'
            logging.info(f"beveragestatistics: Received {received_data}")
            received = ast.literal_eval(received_data)
            for item in received:
                for k, item2 in item.items():
                    if (k.startswith("device_code")):
                        device_code = item2
                    if (k.startswith("TotalCountRcp")):
                        recipes.append(item)
                        summ += item2
            #summ = wm_conn.get_beverages_count()
            ws.close()
    if fake_data:
        create_record = None
        last_record = db_conn.get_last_beverages_log(device[1])
        if last_record is None:
            create_record = db_conn.create_beverages_log(device[1], "0", "1970-01-01 00:00:00", "1970-01-01 00:00:00", "[{'TotalCountRcp': 0}]")
        else:
            create_record = db_conn.create_beverages_log(str(last_record[0]), str(last_record[1]), str(last_record[2]), str(date_formed), str(last_record[5]))
    else:
        if recipes == []:
            create_record = None
            Take_Create_Beverage_Statistics(last_send, device[1])
        else:
            #create_record = db_conn.create_beverages_log(device[1], str(summ), str(date_to_send), str(date_formed), json.dumps(recipes))
            #logging.info(f"result {create_record}")
            last_bev_records = db_conn.get_last_beverages_log(device[1])
            print("last_bev_records")
            print(last_bev_records)
            if last_bev_records is not None:
                last_bev_record = db_conn.get_last_beverages_log_by_id(device[1], last_bev_records[6])
                print("last_bev_record")
                prepend_info = ast.literal_eval(last_bev_record[5])
                last_info = {}
                for item in prepend_info:
                    for rec, it in item.items():
                        last_info[rec] = it
                print(last_info)
                for key in recipes:
                    #print(key)
                    for k, elem in key.items():
                        recipe_str = k.strip("TotalCountRcp")
                        count_bev_recipe = elem
                        recipe_size = re.findall(r'[a-zA-Z]+', recipe_str)[0]
                        recipe_number = re.findall(r'\d+', recipe_str)[0]
                        print(recipe_size)
                        print(count_bev_recipe)
                        print(recipe_number)
                        if last_info[k] == elem:
                            print("GOOD")
                        else:
                            created = {}
                            print("DIFFERENCE")
                            time_now = datetime.fromtimestamp(int(datetime.now().timestamp() // (60 * 60) * 60 * 60 - 1))
                            prev_hour = time_now - timedelta(hours=1)
                            count_of_real_pours = int(elem) - int(last_info[k])
                            pours_detected_in_base = db_conn.get_pours_with_recipeId_and_cup_size(device[1], recipe_number, recipe_size, time_now, prev_hour)
                            if count_of_real_pours != pours_detected_in_base:
                                print("Должно быть")
                                print(count_of_real_pours)
                                print("В базе найдено")
                                print(len(pours_detected_in_base))
                                print(pours_detected_in_base)
                                if len(pours_detected_in_base) < 1 or pours_detected_in_base is None or pours_detected_in_base == 0:
                                    print("Поиск мидла")
                                    middle_recipe = db_conn.get_pours_with_recipeId_and_cup_size(device[1], recipe_number, "M", time_now, prev_hour)
                                    if middle_recipe is None or middle_recipe == []:
                                        from controllers.api.beverages.Drinks import updateDrinks
                                        updateDrinks(device[1], device[2])
                                    if middle_recipe is None or len(middle_recipe) < 1:
                                        recipe_callback = db_conn.getRecipe(device[1], recipe_number)
                                        print(recipe_number)
                                        print(recipe_callback)
                                        if recipe_callback is not None:
                                            middle_recipe = {}
                                            middle_recipe[0] = {}
                                            middle_recipe[0][3] = recipe_callback[3]
                                            middle_recipe[0][4] = recipe_callback[8]
                                            middle_recipe[0][5] = recipe_callback[6]
                                            middle_recipe[0][6] = recipe_callback[10]
                                            middle_recipe[0][7] = recipe_callback[12]
                                            middle_recipe[0][8] = recipe_callback[14]
                                            if middle_recipe is not None and len(middle_recipe) > 1:
                                                db_conn.initPours(device[1], recipe_number, middle_recipe[0][3], recipe_size, middle_recipe[0][4], middle_recipe[0][5], middle_recipe[0][6], middle_recipe[0][7], middle_recipe[0][8])
                                                print("Должен был создаться мидл")
                                                created["aleph_id"] = device[1]
                                                created["recipe_id"] = recipe_number
                                                created["recipe_name"] = middle_recipe[0][3]
                                                created["cup_size"] = recipe_size
                                                created["water"] = middle_recipe[0][4]
                                                created["coffee"] = middle_recipe[0][5]
                                                created["milk"] = middle_recipe[0][6]
                                                created["powder"] = middle_recipe[0][7]
                                                created["foam"] = middle_recipe[0][8]
                                                created["date_formed"] = time_now
                                else:
                                    db_conn.initPours(device[1], recipe_number, pours_detected_in_base[0][3], recipe_size, pours_detected_in_base[0][4], pours_detected_in_base[0][5], pours_detected_in_base[0][6], pours_detected_in_base[0][7], pours_detected_in_base[0][8])
                                    print("Должен был создаться с нужным кап сайзом")
                                    created["aleph_id"] = device[1]
                                    created["recipe_id"] = recipe_number
                                    created["recipe_name"] = pours_detected_in_base[0][3]
                                    created["cup_size"] = recipe_size
                                    created["water"] = pours_detected_in_base[0][4]
                                    created["coffee"] = pours_detected_in_base[0][5]
                                    created["milk"] = pours_detected_in_base[0][6]
                                    created["powder"] = pours_detected_in_base[0][7]
                                    created["foam"] = pours_detected_in_base[0][8]
                                    created["date_formed"] = time_now
                            print("Должен был создаться с нужным кап сайзом")
                            request = f'{WMF_URL}?device={device[1]}&error_id=AT11&date_start={time_now}&date_end={time_now}&duration=0&status=1'
                            response = requests.post(request)
                            print(response)
                            db_conn.create_error_record(device[1], 'AT91')
                            db_conn.close_error_code(device[1], 'AT91')


    return True
    #return create_record


def Send_Statistics(data_info, id_record):
    initialize_logger('beverages_send_worker.py.log')
    logging.info(f"beveragestatistics: GET request: {data_info}")
    url = "https://backend.wmf24.ru/api/beveragestatistics"
    headers = {
        'Content-Type': 'application/json',
        'Serverkey': db_conn.get_encrpt_key()[0]
    }
    response = requests.request("POST", url, headers=headers, data=data_info)
    json_res = response.json()
    now = datetime.fromtimestamp(int((datetime.now()).timestamp()))
    if(json_res["id"]):
        print("UPDATE TIME_FACT_SEND")
        update_record = db_conn.update_beverages_log(id_record, now)
        logging.info(f"update {update_record}")
    else:
        logging.info(f"error unknown id record")
    return response.json()

