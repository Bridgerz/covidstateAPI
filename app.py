from flask import Flask, jsonify
import requests
from flask_apscheduler import APScheduler
from datetime import datetime
import os

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

statesData = []
states = []

def updateData():
    data = requests.get("https://corona.lmao.ninja/historical").json()
    for dict in data:
        if dict['country'] == "usa":
            statesData.append(dict)
            states.append(dict['province'])

app.apscheduler.add_job(id="refresh", func=updateData, trigger='interval', hours=1)

data = requests.get("https://corona.lmao.ninja/historical").json()
for dict in data:
    if dict['country'] == "usa":
        statesData.append(dict)
        states.append(dict['province'])

@app.route("/")
def index():
    return jsonify(statesData)

@app.route("/states")
def returnStates():
    return jsonify(states)

@app.route("/state/<string:state>")
def returnState(state):
    for dict in statesData:
        if dict['province'] == state:
            return jsonify(dict)
    return jsonify([])

# @app.route("/state/<string: state>")
# def state(state):
#     # return that states data

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)