import json
import uuid

from flask import Flask, request
from flask import jsonify
from controllers.db.models import WMFSQLDriver
import sys
#from controllers.machine_installation import test

app = Flask(__name__)
db_conn = WMFSQLDriver()

@app.route('/')
def hello_world():  # put application's code here
    password = request.args.get('action')
    aleph_id = request.args.get("aleph_id")
    machine = db_conn.find_device_by_aleph_id(aleph_id)
    if machine:
        ip = db_conn.get_device_field_by_aleph_id(aleph_id, "address")
        if ip:
            return jsonify(ip), 203
        else:
            return 521
    else:
        return 521


@app.route('/migration_database')
def imported():  # put application's code here
    password = request.args.get('access')
    if password == '123':
        import controllers.apply_migration
        return jsonify("welcome", 200)
    else:
        return 403

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
