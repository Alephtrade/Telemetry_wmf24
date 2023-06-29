import sqlite3
from settings import prod as settings

conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
cur = conn.cursor()

cur.execute('DELETE FROM error_code_stats')
conn.commit()

cur.execute('VACUUM')
conn.commit()

cur.close()
conn.close()
