import sys

sys.path.append("../../")
from db.models import WMFSQLDriver
from settings import prod as settings

WMF_URL = settings.WMF_DATA_URL
WS_URL = settings.WS_URL
DEFAULT_WMF_PARAMS = settings.DEFAULT_WMF_PARAMS
db_conn = WMFSQLDriver()

def get_clean_info():
    data = db_conn.get_last_cleaning_info()
    return data