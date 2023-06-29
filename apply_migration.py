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

cur.close()
conn.close()
