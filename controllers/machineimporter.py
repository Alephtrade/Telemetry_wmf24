import sys
from timezonefinder import TimezoneFinder
from datetime import datetime, timezone
import pytz
sys.path.append("../../")
from controllers.db.models import WMFSQLDriver
import re
import os


db_conn = WMFSQLDriver()

def time_format(list):
    total = int(list[1]) * 60 * 60 + int(list[2]) * 60
    if list[0] == False:
        total = total - total * 2
    return total

def splitter(stroka, operator):
    return stroka.split(operator)
def worker(list):
    obj = TimezoneFinder()
    db_conn.clean_devices()
    split_result = []
    times = []
    positive = True
    for val in list:
        latitude = val["latitude"]
        longitude = val["longitude"]
        result = obj.timezone_at(lng=longitude, lat=latitude)
        dt_to_convert = datetime.utcnow().replace(tzinfo=timezone.utc)
        tz = datetime.strptime(datetime.now(pytz.timezone(result)).strftime("%z"), '%z').tzinfo
        val["timezone"] = str(tz)
        utc_split = splitter(str(tz), "UTC")
        if utc_split[1] != "":
            plus_split = splitter(utc_split[1], "+")
            if 1 in dict(enumerate(plus_split)):
                time = splitter(plus_split[1], ":")
                split_result.append([positive, time[0], time[1]])
            else:
                minus_split = splitter(utc_split[1], "-")
                if 1 in dict(enumerate(minus_split)):
                    positive = False
                    time = splitter(minus_split[1], ":")
                    split_result.append([positive, time[0], time[1]])
        else:
            split_result.append([True, 0, 0])
        for time in split_result:
            val["times"] = time_format(time)
        ping_host = os.system("ping -c 1 -w 1 " + val["address"])
        if ping_host == 0:
            status = 1
        else:
            status = 0
        db_conn.create_device(val["aleph_id"], val["times"], val["address"], val["type"], status)

    return list

#worker()
