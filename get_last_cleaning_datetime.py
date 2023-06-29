from db.models import WMFSQLDriver

db_conn = WMFSQLDriver()
print("Last cleaning date is", db_conn.get_last_record()[2])
db_conn.close()
