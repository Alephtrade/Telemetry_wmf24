import json

from flask import Flask, request
from controllers.test import worker
from flask import jsonify
from controllers.wmf.ssh_send_com import send_wmf_request
import sys

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return jsonify(worker()), 200

@app.route('/console')
def terra():  # put application's code here
    return jsonify(send_wmf_request('{"function": "restart"}'), 200)

@app.route('/migration')
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
