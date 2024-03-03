from datetime import datetime, timedelta


def timedelta_int(delta):
    result = delta.days * 1 + delta.seconds
    return result


time_now = int(datetime.strptime("2024-03-04 01:00:00", '%Y-%m-%d %H:%M:%S').timestamp())
prev_hour = time_now - 3600
date_end_prev_error = prev_hour

wmf_error_time = 0
per_error_time = timedelta()
total_disconnect_time = 0
disconnect_time = timedelta()
prev_disc_id = -1
prev_error_id = -1


unsent_disconnect_records = [(131, '-1', '2024-03-03 10:58:01', None)]
unsent_records = []
wmf_error_count = len(unsent_records)
disconnect_count = len(unsent_disconnect_records)
if len(unsent_disconnect_records) == 0:
    disconnect_start_time = 0
    disconnect_end_time = 0
if len(unsent_disconnect_records) > 0:
    for disconnect_rec_id, disconnect_error_code, disconnect_start_time, disconnect_end_time in unsent_disconnect_records:
        if type(disconnect_start_time) is not datetime and disconnect_start_time is not None:
            disconnect_start_time = int(datetime.strptime(disconnect_start_time, '%Y-%m-%d %H:%M:%S').timestamp())
        if type(disconnect_end_time) is not datetime and disconnect_end_time is not None:
            disconnect_end_time = int(datetime.strptime(disconnect_end_time, '%Y-%m-%d %H:%M:%S').timestamp())
        if disconnect_end_time is None or disconnect_end_time > time_now:  # 3.4.2
            disconnect_end_time = time_now
        if disconnect_start_time is None or disconnect_start_time < prev_hour:  # 3.4.2
            disconnect_start_time = prev_hour
        if len(unsent_records) == 0:
            unsent_records = [(0, '0', None, None)]
        if len(unsent_records) >= 0:
            for rec_id, error_code, start_time, end_time in unsent_records:
                if type(start_time) is not datetime and start_time is not None:
                    start_time = int(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').timestamp())
                if type(end_time) is not datetime and end_time is not None:
                    end_time = int(datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').timestamp())
                if end_time is None or end_time > time_now:
                    end_time = time_now
                if start_time is None or start_time > prev_hour:
                    start_time = prev_hour
                print(start_time)
                print(end_time)
                print(disconnect_start_time)
                print(disconnect_end_time)
                if prev_disc_id != disconnect_rec_id and prev_error_id != rec_id:
                    if start_time <= disconnect_start_time and end_time >= disconnect_end_time:  # 3.4.3
                        total_disconnect_time += abs(disconnect_end_time - disconnect_start_time)
                        if total_disconnect_time < 3600 and wmf_error_time < 3600:
                            #disconnect_count += 1
                            wmf_error_time += abs((disconnect_end_time - end_time) + (disconnect_start_time - start_time))
                        #wmf_error_count += 1
                    elif disconnect_start_time < start_time < disconnect_end_time <= end_time:
                        total_disconnect_time += abs(disconnect_end_time - disconnect_start_time)
                        #disconnect_count += 1
                        wmf_error_time += abs(disconnect_end_time - end_time)
                       # wmf_error_count += 1
                    elif start_time > disconnect_start_time and end_time < disconnect_end_time:
                        total_disconnect_time += abs(disconnect_end_time - disconnect_start_time)
                        #disconnect_count += 1
                    elif start_time > disconnect_end_time and end_time > disconnect_end_time:
                        total_disconnect_time += abs(disconnect_end_time - disconnect_start_time)
                        #disconnect_count += 1
                        wmf_error_time += abs(end_time - start_time)
                        #wmf_error_count += 1
                    elif start_time < disconnect_start_time and end_time < disconnect_end_time:
                        total_disconnect_time += abs(disconnect_end_time - disconnect_start_time)
                        #disconnect_count += 1
                        wmf_error_time += abs(end_time - start_time)
                        #wmf_error_count += 1
                    if total_disconnect_time >= 3600:
                        wmf_error_time = 0
                        total_disconnect_time = 3600
                    else:
                        if wmf_error_time > 3600:
                            wmf_error_time = 3600 - total_disconnect_time
                prev_error_id = rec_id
                prev_disc_id = disconnect_rec_id


wmf_work_time = abs(3600 - wmf_error_time - total_disconnect_time)

print({"time_worked": int(wmf_work_time),
       "wmf_error_count": int(wmf_error_count),
       "wmf_error_time": int(wmf_error_time),
       "stoppage_count": int(disconnect_count),
       "stoppage_time": int(total_disconnect_time)})

