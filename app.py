from flask import Flask
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
    import controllers.apply_migration
    update = controllers.apply_migration
    return jsonify("welcome", 200)

if __name__ == '__main__':
    app.run()
    app.run(host="0.0.0.0", port=80)