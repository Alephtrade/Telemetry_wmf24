import creator
import sender
import sys
sys.path.append("../../")
from db.models import WMFSQLDriver
from datetime import datetime, timedelta

last_send = WMFSQLDriver.get_last_beverages_log()
prev_time_formed = datetime.strptime(last_send[4], "%Y-%m-%d %H:%M:%S")
if datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp())) > prev_time_formed:
    get = creator.Take_Create_Beverage_Statistics()

print(WMFSQLDriver.get_not_sended_beverages_log())
#send = Send_Statistics()