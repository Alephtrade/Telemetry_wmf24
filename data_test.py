from api.datastat import methods
from db.models import WMFSQLDriver

db_driver = WMFSQLDriver()


def are_need_to_create():
    get = methods.get_clean_info()
    return get

print(are_need_to_create())