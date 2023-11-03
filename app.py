from flask import Flask
from controllers.test import worker
from flask import jsonify


app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return jsonify(worker()), 200


if __name__ == '__main__':
    app.run()
