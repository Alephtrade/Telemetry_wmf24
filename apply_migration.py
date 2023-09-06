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

if not does_object_exist('table', 'last_record'):
    stmt = '''
        create table last_record
        (
            id          integer
                constraint last_record_pk
                    primary key,
            cleaning_type text,
            beverages_count integer default 0,
            cleaning_duration real default 0,
            cleaning_datetime text
        )
    '''
    cur.execute(stmt)
    conn.commit()

add_table_column(table_name='last_record', column_name='beverages_count', column_type='integer default 0')
add_table_column(table_name='last_record', column_name='cleaning_duration', column_type='real default 0')
add_table_column(table_name='last_record', column_name='cleaning_datetime', column_type='text')
add_table_column(table_name='error_code_stats', column_name='error_text', column_type='text')
add_table_column(table_name='error_code_stats', column_name='duration_time', column_type='text')

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

if not does_object_exist('table', 'downtimes'):
    stmt = '''
        create table downtimes
        (
            id          integer
                constraint downtimes_pk
                    primary key,
            date_start text,
            date_end   text,
            status        text
        )
    '''
    cur.execute(stmt)
    conn.commit()

add_table_column(table_name='downtimes', column_name='date_start', column_type='text')
add_table_column(table_name='downtimes', column_name='date_end', column_type='text')
add_table_column(table_name='downtimes', column_name='status', column_type='text')

if not does_object_exist('table', 'service_statistics'):
    stmt = '''
        create table service_statistics
        (
            id          integer
                constraint service_statistics_pk
                    primary key,
            date_formed text,
            date_fact_send   text,
            is_sent        text
        )
    '''
    cur.execute(stmt)
    conn.commit()

add_table_column(table_name='service_statistics', column_name='date_formed', column_type='text')
add_table_column(table_name='service_statistics', column_name='date_fact_send', column_type='text')
add_table_column(table_name='service_statistics', column_name='is_sent', column_type='text')

if not does_object_exist('table', 'cleaning_statistic'):
    stmt = '''
        create table cleaning_statistic
        (
            id          integer
                constraint cleaning_statistic_pk
                    primary key,
            cleaning_alias text,
            type_last_cleaning_datetime text,
            type_cleaning_duration  text,
            date_formed text,
            is_sent text
        )
    '''
    cur.execute(stmt)
    conn.commit()

add_table_column(table_name='cleaning_statistic', column_name='cleaning_alias', column_type='text')
add_table_column(table_name='cleaning_statistic', column_name='type_last_cleaning_datetime', column_type='text')
add_table_column(table_name='cleaning_statistic', column_name='type_cleaning_duration', column_type='text')
add_table_column(table_name='cleaning_statistic', column_name='date_formed', column_type='text')
add_table_column(table_name='cleaning_statistic', column_name='is_sent', column_type='text')

if not does_object_exist('table', 'data_statistics'):
    stmt = '''
        create table data_statistics
        (
            id          integer
                constraint data_statistics_pk
                    primary key,
        time_worked text,       
        wmf_error_count text,       
        wmf_error_time text, 
        stoppage_count text,       
        stoppage_time text,       
        date_formed text,
        time_to_send text,
        time_fact_send text,
        is_sent text
        )
    '''
    cur.execute(stmt)
    conn.commit()

add_table_column(table_name='data_statistics', column_name='time_worked', column_type='text')
add_table_column(table_name='data_statistics', column_name='wmf_error_count', column_type='text')
add_table_column(table_name='data_statistics', column_name='wmf_error_time', column_type='text')
add_table_column(table_name='data_statistics', column_name='stoppage_count', column_type='text')
add_table_column(table_name='data_statistics', column_name='stoppage_time', column_type='text')
add_table_column(table_name='data_statistics', column_name='date_formed', column_type='text')
add_table_column(table_name='data_statistics', column_name='time_to_send', column_type='text')
add_table_column(table_name='data_statistics', column_name='time_fact_send', column_type='text')
add_table_column(table_name='data_statistics', column_name='is_sent', column_type='text')


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
