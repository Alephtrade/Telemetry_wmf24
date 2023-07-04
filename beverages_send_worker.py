import ast
from api.beverages import methods
from db.models import WMFSQLDriver
import json

db_driver = WMFSQLDriver()

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
            #k.append(item[5])
            data_info = ast.literal_eval((item[5]))
            for item_info in data_info:
                k.append(item_info)
            #print(json.dumps(item[5]))
            print(json.dumps(k))
            print(methods.Send_Statistics(json.dumps(k)))

print(get_reports_and_send_or_nothing())
