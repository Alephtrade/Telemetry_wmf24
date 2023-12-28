import sqlite3
import logging
import sys
sys.path.append('./')
from datetime import datetime, timedelta
from controllers.settings import prod as settings
from controllers.core.utils import get_curr_time_str


class WMFSQLDriver:

    def __init__(self, db_path=settings.DB_PATH):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)

    def close(self):
        self.connection.close()

    def initRecipe(self, aleph_id, recipe_id, recipe_alias, recipe_string, coffee_count, coffee_weight, water_count, water_weight, milk_count, milk_weight, powder_count, powder_weight, foam_count, foam_weight):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO recipes (aleph_id, recipe_id, recipe_alias, recipe_string, coffee_count, coffee_weight, water_count, water_weight, milk_count, milk_weight, powder_count, powder_weight, foam_count, foam_weight) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(stmt, (aleph_id, recipe_id, recipe_alias, recipe_string, coffee_count, coffee_weight, water_count, water_weight, milk_count, milk_weight, powder_count, powder_weight, foam_count, foam_weight,))
        self.connection.commit()
        cur.close()
    def updateRecipe(self, aleph_id, recipe_id, recipe_alias, recipe_string, coffee_count, coffee_weight, water_count, water_weight, milk_count, milk_weight, powder_count, powder_weight, foam_count, foam_weight):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE recipes 
            SET recipe_alias = ?, recipe_string = ?, coffee_count = ?, coffee_weight = ?, water_count = ?, water_weight = ?, milk_count = ?, milk_weight = ?, powder_count = ?, powder_weight = ?, foam_count = ?, foam_weight = ?
            WHERE aleph_id = ? AND recipe_id = ?
        '''
        cur.execute(stmt, (recipe_alias, recipe_string, coffee_count, coffee_weight, water_count, water_weight, milk_count, milk_weight, powder_count, powder_weight, foam_count, foam_weight, aleph_id, recipe_id))
        self.connection.commit()
        cur.close()
        return stmt
    def getRecipe(self, aleph_id, recipe_id):
        cur = self.connection.cursor()
        stmt = f'''SELECT id, aleph_id, recipe_id, recipe_alias, recipe_string, coffee_count, coffee_weight, water_count, water_weight, milk_count, milk_weight, powder_count, powder_weight, foam_count, foam_weight 
         FROM recipes 
         WHERE aleph_id = "{aleph_id}" AND recipe_id = "{recipe_id}" LIMIT 1'''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        return res

    def initPours(self, aleph_id, recipe_id, recipe_name, cup_size, water_weight, coffee, milk, powder, foam):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO pours (aleph_id, recipe_id, recipe_name, cup_size, water, coffee, milk, powder, foam, date_formed, is_sent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(stmt, (aleph_id, recipe_id, recipe_name, cup_size, water_weight, coffee, milk, powder, foam, datetime.fromtimestamp(int((datetime.now()).timestamp())), 0))
        self.connection.commit()
        cur.close()
    def updatePours(self, aleph_id, recipe_id, recipe_name, cup_size, water_weight, coffee, milk, powder, foam):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE pours 
            SET recipe_alias = ?, recipe_string = ?, coffee_count = ?, coffee_weight = ?, water_count = ?, water_weight = ?, milk_count = ?, milk_weight = ?, powder_count = ?, powder_weight = ?, foam_count = ?, foam_weight = ?
            WHERE aleph_id = ? AND recipe_id = ?
        '''
        cur.execute(stmt, (recipe_alias, recipe_string, coffee_count, coffee_weight, water_count, water_weight, milk_count, milk_weight, powder_count, powder_weight, foam_count, foam_weight, aleph_id, recipe_id))
        self.connection.commit()
        cur.close()
        return stmt

    def get_pours_with_recipeId_and_cup_size(self, aleph_id, recipe_id, cupsize, time_now, prev_hour):
        cur = self.connection.cursor()
        stmt = f'''SELECT id, aleph_id, recipe_id, recipe_name, cup_size, water, coffee, milk, powder, foam, date_formed, is_sent 
         FROM pours 
         WHERE aleph_id = "{aleph_id}" AND recipe_id = "{recipe_id}" AND cup_size = "{cupsize}" AND date_formed > "{prev_hour}" AND date_formed < "{time_now}"'''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        return res

    def get_encrpt_key(self):
        cur = self.connection.cursor()
        stmt = f'''SELECT server_key FROM exchange_php LIMIT 1'''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        return res

    def find_device_by_aleph_id(self, aleph_id):
        cur = self.connection.cursor()
        stmt = f'''SELECT * FROM devices WHERE aleph_id = "{aleph_id}"'''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        if res is not None:
            return True
        else:
            return False

    def find_device_by_full_part_number(self, full_serial):
        cur = self.connection.cursor()
        stmt = f'''SELECT * FROM devices WHERE serial_code = "{full_serial}"'''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        if res is not None:
            return True
        else:
            return False

    def create_device(self, device_aleph_id, device_utc, device_ip, device_model, device_status, full_serial):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO devices (aleph_id, utc, address, type, status, serial_code) VALUES (?, ?, ?, ?, ?, ?)'
        cur.execute(stmt, (device_aleph_id, device_utc, device_ip, device_model, device_status, full_serial,))
        self.connection.commit()
        cur.close()

    def update_device_info(self, aleph_id, utc, address, type, status):
        print(address)
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE devices 
            SET utc = ?, address = ?, type = ?, status = ?
            WHERE aleph_id = ?
        '''
        cur.execute(stmt, (utc, address, type, status, aleph_id))
        self.connection.commit()
        cur.close()
        return stmt

    def update_device_info_by_full_serial(self, full_serial, address, type, status):
        print(address)
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE devices 
            SET address = ?, type = ?, status = ?
            WHERE serial_code = ?
        '''
        cur.execute(stmt, (address, type, status, full_serial))
        self.connection.commit()
        cur.close()
        return stmt

    def update_device_ping_time(self, aleph_id, status, time):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE devices 
            SET status = ?, last_connection = ?
            WHERE aleph_id = ?
        '''
        cur.execute(stmt, (status, time, aleph_id))
        self.connection.commit()
        cur.close()
        return True

    def update_device_ping_time_by_full_serial(self, full_serial, status, time):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE devices 
            SET status = ?, last_connection = ?
            WHERE full_serial = ?
        '''
        cur.execute(stmt, (status, time, full_serial))
        self.connection.commit()
        cur.close()
        return True

    def get_device_field_by_aleph_id(self, aleph_id, field_name):
        cur = self.connection.cursor()
        stmt = f'''
            SELECT {field_name} FROM devices
            WHERE aleph_id = "{aleph_id}"
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        return res

    def clean_devices(self):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id 
            FROM devices 
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        if not res:
            return
        last_id = res[0]
        stmt = 'DELETE FROM devices WHERE id not null '
        cur.execute(stmt)
        self.connection.commit()
        cur.close()

    def get_devices(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, aleph_id, address, utc, last_connection
            FROM devices
            ORDER BY id ASC 
        '''
        cur.execute(stmt)
        res = cur.fetchall()
        logging.info(f'WMFSQLDriver get_devices: {res}')
        cur.close()
        return res

    def delete_device(self, id):
        cur = self.connection.cursor()
        stmt = ''' 
            DELETE FROM devices
            WHERE id = ?
        '''
        cur.execute(stmt, id)
        res = cur.fetchall()
        logging.info(f'WMFSQLDriver get_devices: {res}')
        cur.close()
        return res

    def update_exchange_time(self, minutes):
        cur = self.connection.cursor()
        stmt = 'DELETE FROM exchange_php WHERE id > 0 '
        cur.execute(stmt)
        stmt = 'INSERT INTO exchange_php (minutes) VALUES (?)'
        cur.execute(stmt, (minutes,))
        self.connection.commit()
        cur.close()
        return True

    def get_exchange(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT minutes
            FROM exchange_php
            WHERE id = 1
        '''
        cur.execute(stmt)
        res = cur.fetchall()
        logging.info(f'WMFSQLDriver get_devices: {res}')
        cur.close()
        return res



    #def clean_error_stats(self, error_date):
    #    cur = self.connection.cursor()
    #    stmt = '''
    #        SELECT id
    #        FROM error_code_stats
    #        WHERE error_date = ?
    #        ORDER BY id DESC
    #        LIMIT 1
    #    '''
    #    cur.execute(stmt, (error_date,))
    #    res = cur.fetchone()
    #    if not res:
    #        return
    #    last_id = res[0]
    #    stmt = 'DELETE FROM error_code_stats WHERE id <= ?'
    #    cur.execute(stmt, (last_id,))
    #    self.connection.commit()
    #    cur.close()

    #def clean_tg_reports(self, records_to_keep):
    #    cur = self.connection.cursor()
    #    stmt = '''
    #        SELECT id
    #        FROM tg_reports
    #        ORDER BY id DESC
    #        LIMIT 1
    #    '''
    #    cur.execute(stmt)
    #    res = cur.fetchone()
    #    if not res:
    #        return
    #    last_id = res[0] - records_to_keep
    #    stmt = 'DELETE FROM tg_reports WHERE id <= ?'
    #    cur.execute(stmt, (last_id,))
    #    self.connection.commit()
    #    cur.close()


    def create_error_record(self, aleph_id, error_code):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO error_code_stats (aleph_id, error_code, error_date, start_time, report_sent, duration_time) VALUES (?, ?, ?, ?, 0, 0)'
        current_date = datetime.now()
        error_date = current_date.strftime('%Y-%m-%d')
        start_time = current_date.strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(stmt, (aleph_id, error_code, error_date, start_time,))
        self.connection.commit()
        cur.close()

    def create_cleaning_error_record(self, aleph_id, error_code, start_time):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO error_code_stats (aleph_id, error_code, error_date, start_time, report_sent, duration_time) VALUES (?, ?, ?, ?, 0, 0)'
        current_date = datetime.now()
        error_date = current_date.strftime('%Y-%m-%d')
        cur.execute(stmt, (aleph_id, error_code, error_date, start_time,))
        self.connection.commit()
        cur.close()

    def get_time_to_send_interval(self):
        cur = self.connection.cursor()
        stmt = '''
            SELECT minutes FROM exchange_php
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        return res


    def get_error_prev_record(self, aleph_id, error_code):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id, start_time FROM error_code_stats
            WHERE error_code = ? AND aleph_id = ?
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt, (error_code, aleph_id,))
        res = cur.fetchone()
        cur.close()
        return res

    def close_error_code(self, aleph_id, error_code):
        start_time = self.get_error_prev_record(aleph_id, error_code)
        print(start_time)
        if start_time[1] is None:
            current_date = datetime.now()
            start_time[1] = current_date.strftime('%Y-%m-%d %H:%M:%S')
        print(start_time)
        start_time_formated = int(datetime.strptime(start_time[1], '%Y-%m-%d %H:%M:%S').timestamp())
        duration = str((int(datetime.now().timestamp()) - start_time_formated))
        cur = self.connection.cursor()
        end_time = get_curr_time_str()
        stmt = ''' 
            UPDATE error_code_stats 
            SET end_time = ?, duration_time = ?
            WHERE id = (
                SELECT id
                FROM error_code_stats
                WHERE aleph_id = ? AND error_code = ? AND end_time IS NULL
                ORDER BY id desc
                LIMIT 1
            )
        '''
        cur.execute(stmt, (end_time, duration, aleph_id, error_code))
        self.connection.commit()
        cur.close()

    def get_error_by_id(self, error_id):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id, start_time, error_code FROM error_code_stats
            WHERE id = ?
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt, (error_id,))
        res = cur.fetchone()
        cur.close()
        return res

    def reset_ips(self, aleph_id):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE devices 
            SET address = ""
            WHERE aleph_id = ?
        '''
        cur.execute(stmt, (aleph_id,))
        self.connection.commit()
        cur.close()
        return True

    def reset_all_ips(self):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE devices 
            SET address = ""
        '''
        cur.execute(stmt)
        self.connection.commit()
        cur.close()
        return True

    def close_error_code_by_id(self, aleph_id, last_id):
        that_error_record = self.get_error_by_id(last_id)
        print(last_id)
        print(that_error_record)
        d_id, start_time, error_code = that_error_record
        start_time_formated = int(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').timestamp())
        duration = str((int(datetime.now().timestamp()) - start_time_formated))
        cur = self.connection.cursor()
        end_time = get_curr_time_str()
        stmt = ''' 
            UPDATE error_code_stats 
            SET end_time = ?, duration_time = ?
            WHERE id = ? AND aleph_id = ?
        '''
        cur.execute(stmt, (end_time, duration, last_id, aleph_id))
        self.connection.commit()
        cur.close()
        return True

    def get_error_last_stat_record(self, error_code, aleph_id):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id, end_time FROM error_code_stats
            WHERE error_code = ? AND aleph_id = ?
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt, (error_code, aleph_id,))
        res = cur.fetchone()
        cur.close()
        return res

    def get_error_empty_record(self, aleph_id):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id, end_time, error_code FROM error_code_stats
            WHERE end_time is Null AND aleph_id = ?
            ORDER BY id DESC 
        '''
        cur.execute(stmt, (aleph_id,))
        res = cur.fetchall()
        cur.close()
        return res

    def get_unclosed_error_by_code(self, error_code, aleph_id):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id, error_code FROM error_code_stats
            WHERE error_code = ? AND aleph_id = ? AND end_time is Null
            ORDER BY id DESC
            LIMIT 1
        '''
        cur.execute(stmt, (error_code, aleph_id,))
        res = cur.fetchone()
        cur.close()
        return res

    #def get_last_record(self):
    #    cur = self.connection.cursor()
    #    stmt = '''
    #        SELECT beverages_count, cleaning_duration, cleaning_datetime, cleaning_type FROM last_record WHERE id = 1
    #    '''
    #    cur.execute(stmt)
    #    res = cur.fetchone()
    #    cur.close()
    #    logging.info(f'WMFSQLDriver get_last_record: {res}')
    #    return res

    #def save_last_record(self, key, value):
    #    cur = self.connection.cursor()
    #    record_time = get_curr_time_str()
    #    stmt = f'''
    #        UPDATE last_record
    #        SET {key} = ?, cleaning_datetime = ?
    #        WHERE id = 1
    #    '''
    #    logging.info(f'WMFSQLDriver save_last_record: key = {key}, value = {value}')
    #    cur.execute(stmt, (value, record_time))
    #    self.connection.commit()
    #    cur.close()

    def get_last_clean_or_rins(self, aleph_id, column_namee, alias):
        cur = self.connection.cursor()
        stmt = f''' 
            SELECT id, {column_namee}
            FROM cleaning_statistic 
            WHERE {column_namee} NOT NULL AND cleaning_alias = "{alias}" AND aleph_id = "{aleph_id}"
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        logging.info(f'WMFSQLDriver get_last_record: {res}')
        return res

    def save_clean_or_rins(self, aleph_id, alias, operator, value_column):
        time_now = datetime.fromtimestamp(int(datetime.now().timestamp() // (60 * 60) * 60 * 60))
        cur = self.connection.cursor()
        stmt = f''' 
            UPDATE cleaning_statistic 
            SET {operator} = "{value_column}"
            WHERE aleph_id = "{aleph_id}" AND date_formed = "{time_now}" AND cleaning_alias = "{alias}" AND is_sent = 0
        '''
        logging.info(f'WMFSQLDriver save_last_record: key = {operator}, value = {value_column}')
        cur.execute(stmt)
        self.connection.commit()
        cur.close()

    def save_status_clean_or_rins(self, id_record, operator, value_status):
        time_now = datetime.fromtimestamp(int(datetime.now().timestamp() // (60 * 60) * 60 * 60))
        cur = self.connection.cursor()
        stmt = f''' 
            UPDATE cleaning_statistic 
            SET {operator} = "{value_status}"
            WHERE id = "{id_record}"
        '''
        logging.info(f'WMFSQLDriver save_last_record: key = {operator}, value = {value_status}')
        cur.execute(stmt)
        self.connection.commit()
        cur.close()

    def get_clean_or_rins_to_send(self, aleph_id):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id,
            cleaning_alias, 
            type_last_cleaning_datetime, 
            type_cleaning_duration, 
            date_formed
            FROM cleaning_statistic
            WHERE is_sent = 0 AND aleph_id = ?
            ORDER BY date_formed DESC 
        '''
        cur.execute(stmt, (aleph_id,))
        res = cur.fetchall()
        logging.info(f'WMFSQLDriver get_data_statistics_to_send: {res}')
        cur.close()
        return res

    def get_clean_or_rins_to_queue(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, cleaning_alias
            FROM cleaning_statistic
            WHERE is_sent = 0
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchall()
        logging.info(f'WMFSQLDriver get_data_statistics_to_send: {res}')
        cur.close()
        return res


    def is_record_data_statistics(self, time_delta):
        cur = self.connection.cursor()
        stmt = f''' 
            SELECT id, date_formed
            FROM data_statistics
            WHERE date_formed = ?
        '''
        cur.execute(stmt, (time_delta,))
        res = cur.fetchone()
        cur.close()
        return res

    def save_data_statistics(self, aleph_id, operator, value_column):
        time_now = datetime.fromtimestamp(int((datetime.now()).timestamp() // (60 * 60) * 60 * 60))
        cur = self.connection.cursor()
        record_time = get_curr_time_str()
        stmt = f''' 
            UPDATE data_statistics 
            SET {operator} = "{value_column}"
            WHERE date_formed = "{time_now}" AND aleph_id = "{aleph_id}"
        '''
        logging.info(f'WMFSQLDriver save_last_record: key = {operator}, value = {value_column}')
        cur.execute(stmt)
        self.connection.commit()
        cur.close()

    def save_status_data_statistics(self, id_record, operator, value_status):
        cur = self.connection.cursor()
        stmt = f''' 
            UPDATE data_statistics 
            SET "{operator}" = "{value_status}"
            WHERE id = "{id_record}"
        '''
        logging.info(f'WMFSQLDriver save_last_record: key = {operator}, value = {value_status}')
        cur.execute(stmt)
        self.connection.commit()
        cur.close()

    def create_data_statistics(self, aleph_id, date_formed, time_to_sent):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO data_statistics (aleph_id, date_formed, is_sent, time_to_send) VALUES (?, ?, 0, ?)'
        cur.execute(stmt, (aleph_id, date_formed, time_to_sent,))
        self.connection.commit()
        cur.close()

    def get_last_data_statistics(self, aleph_id):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT time_fact_send
            FROM data_statistics
            WHERE time_fact_send NOT NULL
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt, (aleph_id,))
        res = cur.fetchone()
        logging.info(f'WMFSQLDriver get_last_data_statistics: {res}')
        cur.close()
        return res

    def get_data_statistics_to_send(self, aleph_ids):
        cur = self.connection.cursor()
        stmt = f''' 
            SELECT time_worked, 
            wmf_error_count, 
            wmf_error_time, 
            stoppage_count, 
            stoppage_time, 
            date_formed, 
            time_to_send, 
            time_fact_send,
            is_sent,
            id,
            aleph_id
            FROM data_statistics
            WHERE time_fact_send is NULL AND is_sent == 0 AND aleph_id = "{aleph_ids}"
            ORDER BY id DESC 
        '''
        cur.execute(stmt)
        res = cur.fetchall()
        logging.info(f'WMFSQLDriver get_data_statistics_to_send: {res}')
        cur.close()
        return res

    def get_last_service_statistics(self, aleph_id, date_tod):
        cur = self.connection.cursor()
        stmt = f''' 
            SELECT id, date_formed, is_sent
            FROM service_statistics
            WHERE date_formed = '{date_tod}' AND aleph_id = "{aleph_id}"
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        logging.info(f'WMFSQLDriver get_last_data_statistics: {res}')
        cur.close()
        return res

    def save_status_service_statistics(self, id_record, operator, value_status):
        cur = self.connection.cursor()
        stmt = f''' 
            UPDATE service_statistics 
            SET "{operator}" = "{value_status}"
            WHERE id = "{id_record}"
        '''
        logging.info(f'WMFSQLDriver save_last_record: key = {operator}, value = {value_status}')
        cur.execute(stmt)
        self.connection.commit()
        cur.close()

    def create_service_record(self, aleph_id, date_formed):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO service_statistics (aleph_id, date_formed, date_fact_send, is_sent) VALUES (?, ?, ?, ?)'
        cur.execute(stmt, (aleph_id, date_formed, None, "0",))
        self.connection.commit()
        cur.close()

    def is_record_clean_or_rins(self, time_delta, alias):
        cur = self.connection.cursor()
        stmt = f''' 
            SELECT id, date_formed
            FROM cleaning_statistic
            WHERE date_formed = ? AND cleaning_alias = ?
        '''
        cur.execute(stmt, (time_delta, alias,))
        res = cur.fetchone()
        cur.close()
        return res

    def create_clean_or_rins(self, aleph_id, cleaning_alias, type_last_cleaning_datetime, type_cleaning_duration, date_formed):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO cleaning_statistic (aleph_id, cleaning_alias, type_last_cleaning_datetime, type_cleaning_duration, date_formed, is_sent) VALUES (?, ?, ?, ?, ?, 0)'
        cur.execute(stmt, (aleph_id, cleaning_alias, type_last_cleaning_datetime, type_cleaning_duration, date_formed))
        self.connection.commit()
        cur.close()

    def get_unsent_records(self, aleph_id):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, error_code, start_time, end_time, duration_time 
            FROM error_code_stats WHERE report_sent = 0 AND aleph_id = ?
        '''
        cur.execute(stmt, (aleph_id,))
        res = cur.fetchall()
        cur.close()
        return res

    def get_unsent_records_with_end_time(self, aleph_id):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, error_code, start_time, end_time, duration_time 
            FROM error_code_stats WHERE report_sent = 2 AND end_time is not Null AND aleph_id = ?
        '''
        cur.execute(stmt, (aleph_id,))
        res = cur.fetchall()
        cur.close()
        return res

    def get_error_records(self, prev_hour, now_hour, aleph_id):
        cur = self.connection.cursor()
        stmt = f''' 
            SELECT id, error_code, start_time, end_time 
            FROM error_code_stats 
            WHERE ((end_time > "{prev_hour}" AND end_time <= "{now_hour}")
            OR (start_time >= "{prev_hour}" AND start_time < "{now_hour}")
            OR (start_time <= "{prev_hour}" AND (end_time is NULL OR end_time > "{prev_hour}")))
            AND error_code != "62"
            AND error_code != "-1"
            AND aleph_id = "{aleph_id}"
        '''
        cur.execute(stmt)
        res = cur.fetchall()
        cur.close()
        return res

    def get_all_error_records_by_code(self, aleph_id, prev_hour, now_hour, code):
        cur = self.connection.cursor()
        stmt = f''' 
            SELECT id, error_code, start_time, end_time 
            FROM error_code_stats 
            WHERE ((end_time > "{prev_hour}" AND end_time <= "{now_hour}")
            OR (start_time >= "{prev_hour}" AND start_time < "{now_hour}")
            OR (start_time <= "{prev_hour}" AND (end_time is NULL OR end_time > "{prev_hour}")))
            AND error_code == "{code}"
            AND aleph_id = "{aleph_id}"
        '''
        cur.execute(stmt)
        res = cur.fetchall()
        cur.close()
        return res

    def set_report_sent(self, rec_id):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE error_code_stats 
            SET report_sent = 1
            WHERE id = ?
        '''
        cur.execute(stmt, (rec_id,))
        self.connection.commit()
        cur.close()

    def set_report_pre_sent(self, rec_id):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE error_code_stats 
            SET report_sent = 2
            WHERE id = ?
        '''
        cur.execute(stmt, (rec_id,))
        self.connection.commit()
        cur.close()

    #def get_last_tg_report(self):
    #    cur = self.connection.cursor()
    #    stmt = '''
    #        SELECT id, date_formed, date_sent, body
    #        FROM tg_reports
    #        ORDER BY id DESC
    #        LIMIT 1
    #    '''
    #    cur.execute(stmt)
    #    res = cur.fetchone()
    #    cur.close()
    #    logging.info(f'WMFSQLDriver get_last_tg_report: {res}')
    #    return res
#
    #def get_last_two_tg_reports(self):
    #    cur = self.connection.cursor()
    #    stmt = '''
    #        SELECT id, date_formed, date_sent, body
    #        FROM tg_reports
    #        ORDER BY id DESC
    #        LIMIT 2
    #    '''
    #    cur.execute(stmt)
    #    res = cur.fetchall()
    #    cur.close()
    #    logging.info(f'WMFSQLDriver get_last_two_tg_reports: {res}')
    #    return res
#
    #def create_tg_report(self, date_formed, body):
    #    cur = self.connection.cursor()
    #    stmt = 'INSERT INTO tg_reports (date_formed, body) VALUES (?, ?)'
    #    cur.execute(stmt, (date_formed, body))
    #    self.connection.commit()
    #    cur.close()
#
    #def set_tg_report_body(self, tg_id, date_formed, body):
    #    cur = self.connection.cursor()
    #    stmt = '''
    #        UPDATE tg_reports
    #        SET body = ?, date_formed = ?
    #        WHERE id = ?
    #    '''
    #    cur.execute(stmt, (body, date_formed, tg_id))
    #    self.connection.commit()
    #    cur.close()
#
    #def set_tg_report_sent(self, tg_id, date_sent):
    #    cur = self.connection.cursor()
    #    stmt = '''
    #        UPDATE tg_reports
    #        SET date_sent = ?
    #        WHERE id = ?
    #    '''
    #    cur.execute(stmt, (date_sent, tg_id))
    #    self.connection.commit()
    #    cur.close()

    def create_beverages_log(self, aleph_id, summ, time_to_send, date_formed, recipes):
        cur = self.connection.cursor()
        stmt = '''
        INSERT INTO beverages_log 
        (aleph_id, summ, time_to_send, date_formed, recipes) 
        VALUES (?, ?, ?, ?, ?)
        '''
        cur.execute(stmt, (aleph_id, summ, time_to_send, date_formed, recipes))
        self.connection.commit()
        cur.close()
        return True

    def get_last_beverages_log(self, aleph_id):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT aleph_id, summ, time_to_send, time_fact_send, date_formed, recipes, id
            FROM beverages_log
            WHERE time_fact_send NOT NULL AND aleph_id = ?
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt, (aleph_id,))
        res = cur.fetchone()
        logging.info(f'WMFSQLDriver get_last_beverages_log: {res}')
        cur.close()
        return res

    def get_last_beverages_log_by_id(self, aleph_id, record_id):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT aleph_id, summ, time_to_send, time_fact_send, date_formed, recipes, id
            FROM beverages_log
            WHERE id = ? AND aleph_id = ?
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt, (record_id, aleph_id,))
        res = cur.fetchone()
        logging.info(f'WMFSQLDriver get_last_beverages_log: {res}')
        cur.close()
        return res

    def get_not_sended_beverages_log(self, aleph_id):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT aleph_id, summ, time_to_send, time_fact_send, date_formed, recipes, id
            FROM beverages_log
            WHERE time_fact_send is NULL AND aleph_id = ?
        '''
        cur.execute(stmt, (aleph_id,))
        res = cur.fetchall()
        logging.info(f'WMFSQLDriver get_last_beverages_log: {res}')
        cur.close()
        return res

    def update_beverages_log(self, rec_id, time_fact_send):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE beverages_log 
            SET time_fact_send = ?
            WHERE id = ?
        '''
        cur.execute(stmt, (time_fact_send, rec_id))
        self.connection.commit()
        cur.close()


if __name__ == '__main__':
    db_conn = WMFSQLDriver(db_path='../wmf.db')
    #print(db_conn.get_device_field_by_aleph_id())
