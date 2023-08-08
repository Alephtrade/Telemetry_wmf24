import json
import logging
import requests
from datetime import datetime, timedelta
from db.models import WMFSQLDriver
from wmf.models import WMFMachineStatConnector
from settings import prod as settings
from core.utils import initialize_logger

initialize_logger('check_cleaning_and_rising_state.log')
WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()
wm_conn = WMFMachineStatConnector()

def controller_manager(operator, alias):
    now_of_hour = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
    if operator is not None:
        if operator['durationInSeconds'] and operator['durationInSeconds'] is not None and int(operator['durationInSeconds']) != -1:
            prev_cleaning = db_conn.get_last_clean_or_rins("type_cleaning_duration", alias)
            if prev_cleaning is None:
                prev_cleaning_duration = "0"
            else:
                prev_cleaning_duration = prev_cleaning[1]
            logging.info(f'PartNumber: {wm_conn.part_number}, prev_cleaning_duration: {prev_cleaning_duration}')
            logging.info(f'prev {prev_cleaning_duration} - {alias}')
            logging.info(f'durationInSeconds {operator["durationInSeconds"]}')
            if str(prev_cleaning_duration) != str(operator['durationInSeconds']):
                print("!=")
                db_conn.save_clean_or_rins(alias, "type_cleaning_duration", operator['durationInSeconds'])
                logging.info(f'save new duration {alias}')
                logging.info(f'new time {datetime.now()}')
                type_last_cleaning_datetime = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() - operator['durationInSeconds']))
                return db_conn.create_clean_or_rins(alias, type_last_cleaning_datetime, operator['durationInSeconds'], (datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'))
                send = sender_report()
                logging.info(f'{send}')
            else:
                logging.info(f'{prev_cleaning_duration} = {operator["durationInSeconds"]}')
        else:
            logging.info(f'{operator["durationInSeconds"]} is None or {int(operator["durationInSeconds"]) != -1}')
    else:
        logging.info(f'{operator} is none')



def sender_report():
    data = db_conn.get_clean_or_rins_to_send()
    try:
        with open('/root/wmf_1100_1500_5000_router/part_number.txt') as f:
            part_number = f.read()
    except Exception:
        logging.info(f'{part_number} is none')
    date_formated = []
    if data is not None:
        for item in data:
            date_formated.append({"cleaning_alias": item[1]})
            date_formated.append({"type_last_cleaning_datetime": item[2]})
            date_formated.append({"type_cleaning_duration": item[3]})
            date_formated.append({"date_formed": item[4]})
            date_formated.append({"code": part_number})
            url = "https://wmf24.ru/api/datastat"
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=json.dumps(date_formated))
            logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
            db_conn.save_status_clean_or_rins(item[0], "is_sent", "2")
    else:
        logging.info(f'{data} is none')


get_system_cleaning_state_data = wm_conn.get_system_cleaning_state()
if get_system_cleaning_state_data is not None:
    controller_manager(wm_conn.get_system_cleaning_state(), "general")

get_milk_cleaning_state_data = wm_conn.get_milk_cleaning_state()
if get_milk_cleaning_state_data is not None:
    controller_manager(wm_conn.get_milk_cleaning_state(), "general_milk")

get_foamer_rinsing_state_data = wm_conn.get_foamer_rinsing_state()
if get_foamer_rinsing_state_data is not None:
    controller_manager(wm_conn.get_foamer_rinsing_state(), "foamer")

get_milk_replacement_state_data = wm_conn.get_milk_replacement_state()
if get_milk_replacement_state_data is not None:
    controller_manager(wm_conn.get_milk_replacement_state(), "milk_replacement")

get_mixer_rinsing_state_data = wm_conn.get_mixer_rinsing_state()
if get_mixer_rinsing_state_data is not None:
    controller_manager(wm_conn.get_mixer_rinsing_state(), "general_mixer")

get_milk_mixer_warm_rinsing_state_data = wm_conn.get_milk_mixer_warm_rinsing_state()
if get_milk_mixer_warm_rinsing_state_data is not None:
    controller_manager(wm_conn.get_milk_mixer_warm_rinsing_state(), "milk_mixer_warm")

get_ffc_filter_replacement_state_data = wm_conn.get_ffc_filter_replacement_state()
if get_ffc_filter_replacement_state_data is not None:
    controller_manager(wm_conn.get_ffc_filter_replacement_state(), "ffc_filter")

sender_report()