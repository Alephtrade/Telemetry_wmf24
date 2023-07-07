import sqlite3
import logging
from datetime import datetime, timedelta
from settings import prod as settings
from core.utils import get_curr_time_str


class WMFSQLDriver:
    def __init__(self, db_path=settings.DB_PATH):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)

    def close(self):
        self.connection.close()

    def clean_error_stats(self, error_date):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id 
            FROM error_code_stats 
            WHERE error_date = ? 
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt, (error_date,))
        res = cur.fetchone()
        if not res:
            return
        last_id = res[0]
        stmt = 'DELETE FROM error_code_stats WHERE id <= ?'
        cur.execute(stmt, (last_id,))
        self.connection.commit()
        cur.close()

    def clean_tg_reports(self, records_to_keep):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id 
            FROM tg_reports 
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        if not res:
            return
        last_id = res[0] - records_to_keep
        stmt = 'DELETE FROM tg_reports WHERE id <= ?'
        cur.execute(stmt, (last_id,))
        self.connection.commit()
        cur.close()

    def create_error_record(self, error_code, error_text='Неизвестная ошибка'):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO error_code_stats (error_code, error_date, start_time, error_text) VALUES (?, ?, ?, ?)'
        current_date = datetime.now() + timedelta(hours=3)
        error_date = current_date.strftime('%Y-%m-%d')
        start_time = current_date.strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(stmt, (error_code, error_date, start_time, error_text))
        self.connection.commit()
        cur.close()

    def close_error_code(self, error_code):
        cur = self.connection.cursor()
        end_time = get_curr_time_str()
        stmt = ''' 
            UPDATE error_code_stats 
            SET end_time = ?
            WHERE id = (
                SELECT id
                FROM error_code_stats
                WHERE error_code = ? AND end_time IS NULL
                ORDER BY id desc
                LIMIT 1
            )
        '''
        cur.execute(stmt, (end_time, error_code))
        self.connection.commit()
        cur.close()

    def close_error_code_by_id(self, last_id):
        cur = self.connection.cursor()
        end_time = get_curr_time_str()
        stmt = ''' 
            UPDATE error_code_stats 
            SET end_time = ?
            WHERE id = ?
        '''
        cur.execute(stmt, (end_time, last_id))
        self.connection.commit()
        cur.close()

    def get_error_last_stat_record(self, error_code):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id, end_time FROM error_code_stats
            WHERE error_code = ?
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt, (error_code,))
        res = cur.fetchone()
        cur.close()
        return res

    def get_last_record(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT beverages_count, cleaning_duration, cleaning_datetime, cleaning_type FROM last_record WHERE id = 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        logging.info(f'WMFSQLDriver get_last_record: {res}')
        return res

    def save_last_record(self, key, value):
        cur = self.connection.cursor()
        record_time = get_curr_time_str()
        stmt = f''' 
            UPDATE last_record 
            SET {key} = ?, record_time = ?
            WHERE id = 1
        '''
        logging.info(f'WMFSQLDriver save_last_record: key = {key}, value = {value}')
        cur.execute(stmt, (value, record_time))
        self.connection.commit()
        cur.close()

    def get_last_clean_or_rins(self, column_namee):
        cur = self.connection.cursor()
        stmt = f''' 
            SELECT id, {column_namee}
            FROM data_statistics 
            WHERE ? NOT NULL
        '''
        cur.execute(stmt, (column_namee,))
        res = cur.fetchone()
        cur.close()
        logging.info(f'WMFSQLDriver get_last_record: {res}')
        return res

    def save_clean_or_rins(self, operator, value_column):
        time_now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
        cur = self.connection.cursor()
        record_time = get_curr_time_str()
        stmt = f''' 
            UPDATE data_statistics 
            SET {operator} = "{value_column}"
            WHERE date_formed = "{time_now}"
        '''
        logging.info(f'WMFSQLDriver save_last_record: key = {operator}, value = {value_column}')
        cur.execute(stmt)
        self.connection.commit()
        cur.close()


    def is_record_clean_or_rins(self, time_delta):
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

    def create_clean_or_rins(self, date_formed):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO data_statistics (date_formed) VALUES (?)'
        cur.execute(stmt, (date_formed,))
        self.connection.commit()
        cur.close()

    def get_last_cleaning_info(self):
        time_now = datetime.fromtimestamp(int((datetime.now() + timedelta(hours=3)).timestamp() // (60 * 60) * 60 * 60))
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT last_general_cleaning_datetime, 
            general_cleaning_duration, 
            next_general_cleaning_datetime, 
            last_milk_cleaning_datetime, 
            general_milk_cleaning_duration, 
            next_milk_cleaning_datetime, 
            last_foamer_rising_datetime, 
            general_foamer_rising_duration, 
            next_foamer_rising_datetime, 
            last_milk_replacement_datetime, 
            general_milk_replacement_duration, 
            next_milk_replacement_datetime, 
            last_mixer_rinsing_datetime, 
            general_mixer_rinsing_duration, 
            next_mixer_rinsing_datetime, 
            last_milk_mixer_warm_rinsing_datetime, 
            general_milk_mixer_warm_rinsing_duration, 
            next_milk_mixer_warm_rinsing_datetime, 
            last_ffc_filter_replacement_datetime, 
            general_ffc_filter_replacement_duration, 
            next_ffc_filter_replacement_datetime 
            FROM data_statistics 
            WHERE date_formed = ?
        '''
        cur.execute(stmt, (time_now,))
        res = cur.fetchone()
        cur.close()
        logging.info(f'WMFSQLDriver get_last_record: {res}')
        return res

    def get_unsent_records(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, error_code, start_time, end_time, error_text 
            FROM error_code_stats WHERE report_sent = 0
        '''
        cur.execute(stmt)
        res = cur.fetchall()
        cur.close()
        return res

    def get_error_records(self, date_and_time_start, date_and_time_end):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, error_code, start_time, end_time, error_text 
            FROM error_code_stats WHERE start_time > ? AND end_time < ?
        '''
        cur.execute(stmt, (date_and_time_start, date_and_time_end))
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

    def get_last_tg_report(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, date_formed, date_sent, body 
            FROM tg_reports
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        cur.close()
        logging.info(f'WMFSQLDriver get_last_tg_report: {res}')
        return res

    def get_last_two_tg_reports(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, date_formed, date_sent, body 
            FROM tg_reports
            ORDER BY id DESC 
            LIMIT 2
        '''
        cur.execute(stmt)
        res = cur.fetchall()
        cur.close()
        logging.info(f'WMFSQLDriver get_last_two_tg_reports: {res}')
        return res

    def create_tg_report(self, date_formed, body):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO tg_reports (date_formed, body) VALUES (?, ?)'
        cur.execute(stmt, (date_formed, body))
        self.connection.commit()
        cur.close()

    def set_tg_report_body(self, tg_id, date_formed, body):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE tg_reports 
            SET body = ?, date_formed = ?
            WHERE id = ?
        '''
        cur.execute(stmt, (body, date_formed, tg_id))
        self.connection.commit()
        cur.close()

    def set_tg_report_sent(self, tg_id, date_sent):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE tg_reports 
            SET date_sent = ?
            WHERE id = ?
        '''
        cur.execute(stmt, (date_sent, tg_id))
        self.connection.commit()
        cur.close()

    def create_downtime(self, date_start, status):
        cur = self.connection.cursor()
        stmt = 'INSERT INTO machine_activity (date_start, status) VALUES (?, ?)'
        cur.execute(stmt, (date_start, status))
        self.connection.commit()
        cur.close()

    def get_last_downtime(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, date_start, date_end, status 
            FROM machine_activity
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        logging.info(f'WMFSQLDriver get_last_downtime: {res}')
        cur.close()
        return res

    def update_downtime(self, id, date_end, status):
        cur = self.connection.cursor()
        stmt = ''' 
            UPDATE machine_activity 
            SET date_end = ?, status = ?
            WHERE id = ?
        '''
        cur.execute(stmt, (date_end, status, id))
        self.connection.commit()
        cur.close()

    def create_beverages_log(self, device_code, summ, time_to_send, date_formed, recipes):
        cur = self.connection.cursor()
        stmt = '''
        INSERT INTO beverages_log 
        (device_code, summ, time_to_send, date_formed, recipes) 
        VALUES (?, ?, ?, ?, ?)
        '''
        cur.execute(stmt, (device_code, summ, time_to_send, date_formed, recipes))
        self.connection.commit()
        cur.close()

    def get_last_beverages_log(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT device_code, summ, time_to_send, time_fact_send, date_formed, recipes
            FROM beverages_log
            WHERE time_fact_send NOT NULL
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt)
        res = cur.fetchone()
        logging.info(f'WMFSQLDriver get_last_beverages_log: {res}')
        cur.close()
        return res

    def get_not_sended_beverages_log(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT device_code, summ, time_to_send, time_fact_send, date_formed, recipes, id
            FROM beverages_log
            WHERE time_fact_send is NULL
        '''
        cur.execute(stmt)
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
    print(db_conn.get_last_record())
