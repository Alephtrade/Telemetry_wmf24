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
    return jsonify(password), 203


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
