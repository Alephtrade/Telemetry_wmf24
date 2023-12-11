import json
import logging
import requests
from datetime import datetime, timedelta
import sys
sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.db.models import WMFSQLDriver
from controllers.wmf.models import WMFMachineStatConnector
from controllers.settings import prod as settings
from controllers.core.utils import initialize_logger

initialize_logger('check_cleaning_and_rising_state.log')
WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def controller_manager(device, operator, alias):
    if operator is not None:
        print(operator)
        if operator['durationInSeconds'] and operator['durationInSeconds'] is not None and int(operator['durationInSeconds']) != -1:
            prev_cleaning = db_conn.get_last_clean_or_rins(device[1], "type_cleaning_duration", alias)
            if prev_cleaning is None:
                prev_cleaning_duration = "0"
            else:
                prev_cleaning_duration = prev_cleaning[1]
            logging.info(f'aleph_id: {device[1]}, prev_cleaning_duration: {prev_cleaning_duration}')
            logging.info(f'prev {prev_cleaning_duration} - {alias}')
            logging.info(f'durationInSeconds {operator["durationInSeconds"]}')
            if str(prev_cleaning_duration) != str(operator['durationInSeconds']):
                print("!=")
                db_conn.save_clean_or_rins(device[1], alias, "type_cleaning_duration", operator['durationInSeconds'])
                logging.info(f'save new duration {alias}')
                logging.info(f'new time {datetime.now()}')
                type_last_cleaning_datetime = datetime.fromtimestamp(int(datetime.now().timestamp() - operator['durationInSeconds']))
                return db_conn.create_clean_or_rins(device[1], alias, type_last_cleaning_datetime, operator['durationInSeconds'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                logging.info(f'{prev_cleaning_duration} = {operator["durationInSeconds"]}')
        else:
            logging.info(f'{operator["durationInSeconds"]} is None or {int(operator["durationInSeconds"]) != -1}')
    else:
        logging.info(f'{operator} is none')



def sender_report(device):
    data = db_conn.get_clean_or_rins_to_send(device[1])
    date_formatted = []
    if data is not None:
        for item in data:
            date_formatted.append({"cleaning_alias": item[1]})
            date_formatted.append({"type_last_cleaning_datetime": item[2]})
            date_formatted.append({"type_cleaning_duration": item[3]})
            date_formatted.append({"date_formed": item[4]})
            date_formatted.append({"device": device[1]})
            url = "https://backend.wmf24.ru/api/datastat"
            headers = {
                'Content-Type': 'application/json',
                'Serverkey': db_conn.get_encrpt_key()[0]
            }
            response = requests.request("POST", url, headers=headers, data=json.dumps(date_formatted))
            logging.info(f"WMFMachineStatConnector: GET response: {response.text}")
            db_conn.save_status_clean_or_rins(item[0], "is_sent", "2")
    else:
        logging.info(f'{data} is none')


devices = db_conn.get_devices()
for device in devices:
    wm_conn = WMFMachineStatConnector(device[1], device[2])
    get_system_cleaning_state_data = wm_conn.get_system_cleaning_state()
    if get_system_cleaning_state_data is not None:
        controller_manager(device, wm_conn.get_system_cleaning_state(), "general")

    get_milk_cleaning_state_data = wm_conn.get_milk_cleaning_state()
    if get_milk_cleaning_state_data is not None:
        controller_manager(device, wm_conn.get_milk_cleaning_state(), "general_milk")

    get_foamer_rinsing_state_data = wm_conn.get_foamer_rinsing_state()
    if get_foamer_rinsing_state_data is not None:
        controller_manager(device, wm_conn.get_foamer_rinsing_state(), "foamer")

    get_milk_replacement_state_data = wm_conn.get_milk_replacement_state()
    if get_milk_replacement_state_data is not None:
        controller_manager(device, wm_conn.get_milk_replacement_state(), "milk_replacement")

    get_mixer_rinsing_state_data = wm_conn.get_mixer_rinsing_state()
    if get_mixer_rinsing_state_data is not None:
        controller_manager(device, wm_conn.get_mixer_rinsing_state(), "general_mixer")

    get_milk_mixer_warm_rinsing_state_data = wm_conn.get_milk_mixer_warm_rinsing_state()
    if get_milk_mixer_warm_rinsing_state_data is not None:
        controller_manager(device, wm_conn.get_milk_mixer_warm_rinsing_state(), "milk_mixer_warm")

    get_ffc_filter_replacement_state_data = wm_conn.get_ffc_filter_replacement_state()
    if get_ffc_filter_replacement_state_data is not None:
        controller_manager(device, wm_conn.get_ffc_filter_replacement_state(), "ffc_filter")

    wm_conn.close()
    sender_report(device)
