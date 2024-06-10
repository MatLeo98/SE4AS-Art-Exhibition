import json

import requests
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.secret_key = 'B;}}S5Cx@->^^"hQT{T,GJ@YI*><17'


@app.route("/config/modes/<mode>", methods=["GET"])
def get_mode(mode):
    with open('config.prop', 'r') as f:
        modes = json.loads(f.read())['mode']

    resp = jsonify(success=True, error="none", data=modes[mode])
    resp.status_code = 200
    return resp

@app.route("/config/modes/all", methods=["GET"])
def get_modes_json():
    with open('config.prop', 'r') as f:
        modes = json.loads(f.read())['mode']

    resp = jsonify(success=True, error="none", modes=modes)
    resp.status_code = 200
    return resp

@app.route("/config/targets/<measurement>", methods=["GET"])
def get_target(measurement):
    with open('config.prop', 'r') as f:
        targets = json.loads(f.read())['target']

    resp = jsonify(success=True, error="none", data=targets[measurement])
    resp.status_code = 200
    return resp

@app.route("/config/targets/all", methods=["GET"])
def get_targets_json():
    with open('config.prop', 'r') as f:
        targets = json.loads(f.read())['target']

    resp = jsonify(success=True, error="none", targets=targets)
    resp.status_code = 200
    return resp

if __name__ == "__main__":
    app.run(debug=True,host='173.20.0.108', port=5008)