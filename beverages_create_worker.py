from api.beverages import methods
from db.models import WMFSQLDriver
from datetime import datetime, timedelta

db_driver = WMFSQLDriver()

def are_need_to_create():
    last_send = db_driver.get_last_beverages_log()
    if last_send is None:
        now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp()))
        get = methods.Take_Create_Beverage_Statistics(now)
    else:
        get = methods.Take_Create_Beverage_Statistics(last_send[3])
        print(get)


print(are_need_to_create())
