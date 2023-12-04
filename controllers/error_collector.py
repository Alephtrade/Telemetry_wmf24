import atexit
import json
import requests
import logging
import threading
from datetime import timedelta
from timeloop import Timeloop
import sys

sys.path.append('./')
sys.path.append('/var/www/Telemetry_wmf24/')
from controllers.core.utils import initialize_logger, print_exception, get_env_mode, get_part_number_local
from controllers.wmf.models import WMFMachineErrorConnector
from controllers.settings import prod as settings
from controllers.db.models import WMFSQLDriver

db_conn = WMFSQLDriver()
devices = db_conn.get_devices()
for device in devices:
    wmf_conn = WMFMachineErrorConnector(device[1], device[2])
    print(wmf_conn)

