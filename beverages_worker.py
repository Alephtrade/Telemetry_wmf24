from api.beverages import methods
from db.models import WMFSQLDriver
from datetime import datetime, timedelta

db_driver = WMFSQLDriver()

def are_need_to_create():
    last_send = db_driver.get_last_beverages_log()
    if last_send is not None:
        date_formed = last_send[4]
        prev_time_formed = datetime.strptime(date_formed, "%Y-%m-%d %H:%M:%S")
        if datetime.fromtimestamp(int((datetime.now() + timedelta(hours=1)).timestamp())) >= prev_time_formed:
            #get = methods.Take_Create_Beverage_Statistics()
            #print(get)
    else:
        #get = methods.Take_Create_Beverage_Statistics()
        #print(get)

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
            k.append({"recipes": item[5]})

            print(k)
            print(methods.Send_Statistics(k))

print(are_need_to_create())
#print(get_reports_and_send_or_nothing())
