from api.beverages import methods
from db.models import WMFSQLDriver
from datetime import datetime, timedelta

db_driver = WMFSQLDriver()


def are_need_to_create():
    last_send = db_driver.get_last_beverages_log()
    if last_send is None:
        get = methods.Take_Create_Beverage_Statistics()
        #print("LAST SEND IS NONE")
    else:
        #print("LAST SEND")
        #print(last_send[2])
        date_formed = last_send[2]
        prev_time_formed = datetime.strptime(date_formed, "%Y-%m-%d %H:%M:%S")
        #print("Текущее время")
        #print(datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())))
        #print("Время последней отправки")
        #print(prev_time_formed)
        if datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())) >= prev_time_formed:
            get = methods.Take_Create_Beverage_Statistics()
            #print("Создал запись")
            print(get)


print(are_need_to_create())
