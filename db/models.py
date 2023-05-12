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
            cur.close()
            return
        last_id = res[0]
        stmt = 'DELETE FROM error_code_stats WHERE id <= ?'
        cur.execute(stmt, (last_id, ))
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
            cur.close()
            return
        last_id = res[0] - records_to_keep
        stmt = 'DELETE FROM tg_reports WHERE id <= ?'
        cur.execute(stmt, (last_id, ))
        self.connection.commit()
        cur.close()

    def create_error_record(self, error_code, error_text='Неизвестная ошибка'):
        cur = self.connection.cursor()
        current_date = datetime.now() + timedelta(hours=3)
        error_date = current_date.strftime('%Y-%m-%d')
        start_time = current_date.strftime('%Y-%m-%d %H:%M:%S')
        stmt = ''' 
            SELECT id
            FROM error_code_stats
            WHERE error_code = ? AND end_time IS NULL
            ORDER BY id desc
            LIMIT 1
        '''
        cur.execute(stmt, (error_code,))
        res = cur.fetchone()
        if res:
            stmt = '''
                UPDATE error_code_stats 
                SET error_date = ?, start_time = ?
                WHERE id = ?
            '''
            cur.execute(stmt, (error_date, start_time, res[0]))
        else:
            stmt = 'INSERT INTO error_code_stats (error_code, error_date, start_time, error_text) VALUES (?, ?, ?, ?)'
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
        return end_time

    def get_error_last_stat_record(self, error_code):
        cur = self.connection.cursor()
        stmt = '''
            SELECT id, end_time FROM error_code_stats
            WHERE error_code = ?
            ORDER BY id DESC 
            LIMIT 1
        '''
        cur.execute(stmt, (error_code, ))
        res = cur.fetchone()
        cur.close()
        return res

    def get_last_record(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT beverages_count, cleaning_duration, cleaning_datetime FROM last_record WHERE id = 1
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

    def get_unsent_records(self):
        cur = self.connection.cursor()
        stmt = ''' 
            SELECT id, error_code, start_time, end_time, error_text FROM error_code_stats WHERE report_sent = 0
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
        cur.execute(stmt, (rec_id, ))
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

    def do_vacuum(self):
        cur = self.connection.cursor()
        cur.execute('VACUUM')
        self.connection.commit()
        cur.close()


if __name__ == '__main__':
    db_conn = WMFSQLDriver(db_path='../wmf.db')
    print(db_conn.get_last_record())
