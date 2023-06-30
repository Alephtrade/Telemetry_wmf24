from api.beverages import creator
from api.beverages import sender
import sys
from db.models import WMFSQLDriver
from datetime import datetime, timedelta
from core.utils import initialize_logger
import logging


db_driver = WMFSQLDriver()

def are_need_to_create():
    last_send = db_driver.get_last_beverages_log()
    if last_send is not None:
        date_formed = last_send[4]
        prev_time_formed = datetime.strptime(date_formed, "%Y-%m-%d %H:%M:%S")
        if datetime.fromtimestamp(int((datetime.now() + timedelta(hours=1)).timestamp())) >= prev_time_formed:
            get = creator.Take_Create_Beverage_Statistics()
            print(get)
    else:
        get = creator.Take_Create_Beverage_Statistics()
        print(get)

def get_reports_and_send_or_nothing():
    dict = []
    receive_data = db_driver.get_not_sended_beverages_log()
    if(receive_data == []):
        return False
    else:
        for item in receive_data:
            dict.append(item)
            print(item)
            send = sender.Send_Statistics(item)
            initialize_logger('Send_Statistics.txt')
            logging.info(f"beveragestatistics: GET request: {send}")

#are_need_to_create()
#print(get_reports_and_send_or_nothing())
#