from datetime import datetime, timedelta
from db.models import WMFSQLDriver
from core.utils import get_env_mode
if get_env_mode() == 'prod':
    from settings import prod as settings
else:
    from settings import test as settings

db_driver = WMFSQLDriver()

error_date = (datetime.now() + timedelta(hours=3) - timedelta(days=settings.CLEAN_DB_DAYS)).strftime('%Y-%m-%d')
db_driver.clean_error_stats(error_date)
db_driver.clean_tg_reports(settings.TELEGRAM_REPORT_RECORDS_TO_KEEP)

db_driver.close()
