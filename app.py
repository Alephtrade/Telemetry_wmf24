import json
import uuid
import websocket
from flask import Flask, request
from flask import jsonify, abort
from collections import deque
from controllers.db.models import WMFSQLDriver
import sys
#from controllers.machine_installation import test

app = Flask(__name__)
db_conn = WMFSQLDriver()


@app.route('/')
def imported():  # put application's code here
    abort(401)


@app.route('/remote_action')
def hello_world():  # put application's code here
    #return jsonify("1"), 203
    action = request.args.get('action')
    aleph_id = request.args.get("aleph_id")
    machine = db_conn.find_device_by_aleph_id(aleph_id)
    if machine:
        ip = db_conn.get_device_field_by_aleph_id(aleph_id, "address")
        if ip:
            WS_URL = f'ws://{ip[0]}:25000/'
            try:
                ws = websocket.create_connection(WS_URL, timeout=5)
            except Exception:
                return jsonify("false connection"), 521
            if action == "block":
                machine_status = db_conn.get_machine_block_status(aleph_id)
                if request.args.get("block") == "1":
                    db_conn.set_machine_block_status(aleph_id, "1")
                    #  БЛОКИРОВАТЬ
                else:
                    db_conn.set_machine_block_status(aleph_id, "0")
                    #  РАЗБЛОКИРОВАТЬ
            else:
                request_to_machine = json.dumps({'function': action})
                ws.send(request_to_machine)
                received_data = ws.recv()
                # return print(received_drinks)
                received_answer = deque(json.loads(received_data))
                formatted_answer = {}
                for var_drinks in list(received_answer):
                    for i_drinks in var_drinks:
                        formatted_answer[i_drinks] = var_drinks[i_drinks]
                        if formatted_answer["returnvalue"] is not None and formatted_answer["returnvalue"] == 0:
                            return jsonify([received_data, request_to_machine]), 203
                        else:
                            return jsonify("wrong machine answer"), 521
        else:
            return jsonify("ip null"), 521
    else:
        return jsonify("machine null"), 521


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
