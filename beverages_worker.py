from api.beverages import methods
from db.models import WMFSQLDriver
from datetime import datetime, timedelta
import json


db_driver = WMFSQLDriver()

def are_need_to_create():
    last_send = db_driver.get_last_beverages_log()
    if last_send is None:
        get = methods.Take_Create_Beverage_Statistics()
        print("LAST SEND IS NONE")
    else:
        print("LAST SEND")
        print(last_send[2])
        date_formed = last_send[2]
        prev_time_formed = datetime.strptime(date_formed, "%Y-%m-%d %H:%M:%S")
        print("Текущее время")
        print(datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())))
        print("Время последней отправки")
        print(prev_time_formed)
        if datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())) >= prev_time_formed:
            get = methods.Take_Create_Beverage_Statistics()
            print("Создал запись")
            print(get)


def get_reports_and_send_or_nothing():
    k = []
    receive_data = db_driver.get_not_sended_beverages_log()
    if(receive_data == []):
        return False
    else:
        for item in receive_data:
            k.append({"device_code": item[0]})
            k.append({"summ": item[1]})
            k.append({"time_to_send": item[2]})
            k.append({"is_send": item[3]})
            k.append({"date_formed": item[4]})
            k.append(item[5])
            print(json.dumps(item[5]))
            print(json.dumps(k))
            print(methods.Send_Statistics(json.dumps(k)))


print(are_need_to_create())
print(get_reports_and_send_or_nothing())
