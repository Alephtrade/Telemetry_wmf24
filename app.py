import json
import uuid

from flask import Flask, request
from controllers.test import worker
from flask import jsonify
from controllers.db.models import WMFSQLDriver
from controllers.wmf.ssh_send_com import send_wmf_request
import sys
from controllers.machine_installation import test

app = Flask(__name__)
db_conn = WMFSQLDriver()

@app.route('/')
def hello_world():  # put application's code here
    creator = db_conn.create_device(str(uuid.uuid4()), str(34), str("10.8.0.1"),
                          str("1500S+",), str(1))
    return jsonify(creator), 200

@app.route('/test')
def terra():  # put application's code here
    return jsonify("123")
    #return jsonify(send_wmf_request('{"function": "restart"}'), 200)


@app.route('/migration_database')
def imported():  # put application's code here
    password = request.args.get('access')
    if password == '123':
        import controllers.apply_migration
        return jsonify("welcome", 200)
    else:
        return 403
@app.route('/applymachines' , methods = ['POST'])
def imported2():  # put application's code here
    content = request.data
    decoded_data = json.loads(content)
    parse_imported_machines = decoded_data["machines"]
    from controllers.machineimporter import worker
    result = worker(parse_imported_machines)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
