import sqlite3
from settings import prod as settings


def does_column_exist(table_name, column_name):
    cur.execute(f'PRAGMA table_info (\'{table_name}\')')
    rows = cur.fetchall()
    for r in rows:
        if r[1] == column_name:
            return True
    return False


def does_object_exist(object_type, table_name):
    cur.execute(f'SELECT 1 FROM sqlite_master WHERE type=\'{object_type}\' and name=\'{table_name}\'')
    row = cur.fetchone()
    return bool(row)


def add_table_column(table_name, column_name, column_type):
    if not does_column_exist(table_name, column_name):
        cur.execute(f'alter table {table_name} add {column_name} {column_type};')
        conn.commit()


conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
cur = conn.cursor()

add_table_column(table_name='last_record', column_name='beverages_count', column_type='integer default 0')
add_table_column(table_name='last_record', column_name='cleaning_duration', column_type='real default 0')
add_table_column(table_name='last_record', column_name='cleaning_datetime', column_type='text')
add_table_column(table_name='error_code_stats', column_name='error_text', column_type='text')

if not does_object_exist('table', 'tg_reports'):
    stmt = '''
        create table tg_reports
        (
            id          integer
                constraint tg_reports_pk
                    primary key,
            date_formed text,
            date_sent   text,
            body        text
        )
    '''
    cur.execute(stmt)
    conn.commit()

if not does_object_exist('table', 'data_statistics'):
    stmt = '''
        create table data_statistics
        (
            id          integer
                constraint data_statistics_pk
                    primary key,
            time_worked text,
            error_count text,
            error_time text,
            last_cleaning_datetime text,
            cleaning_duration text, 
            next_cleaning_datetime text,
            beverages_count text,
            date_formed text
        )
    '''
    cur.execute(stmt)
    conn.commit()

add_table_column(table_name='data_statistics', column_name='time_worked', column_type='text')
add_table_column(table_name='data_statistics', column_name='error_count', column_type='text')
add_table_column(table_name='data_statistics', column_name='error_time', column_type='text')
add_table_column(table_name='data_statistics', column_name='error_time', column_type='text')
add_table_column(table_name='data_statistics', column_name='last_cleaning_datetime', column_type='text')
add_table_column(table_name='data_statistics', column_name='cleaning_duration', column_type='text')
add_table_column(table_name='data_statistics', column_name='next_cleaning_datetime', column_type='text')
add_table_column(table_name='data_statistics', column_name='beverages_count', column_type='text')
add_table_column(table_name='data_statistics', column_name='date_formed', column_type='text')

if not does_object_exist('table', 'beverages_log'):
    stmt = '''
        create table beverages_log
        (
            id          integer
                constraint beverages_log_pk
                    primary key,
            device_code text,
            summ   text,
            time_to_send        text
            time_fact_send     text
            date_formed     text
            recipes text
        )
    '''
    cur.execute(stmt)
    conn.commit()

add_table_column(table_name='beverages_log', column_name='device_code', column_type='text')
add_table_column(table_name='beverages_log', column_name='summ', column_type='text')
add_table_column(table_name='beverages_log', column_name='time_to_send', column_type='text')
add_table_column(table_name='beverages_log', column_name='time_fact_send', column_type='text')
add_table_column(table_name='beverages_log', column_name='date_formed', column_type='text')
add_table_column(table_name='beverages_log', column_name='recipes', column_type='text')

cur.close()
conn.close()
