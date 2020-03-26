from flask import Flask, jsonify
import requests
from flask_apscheduler import APScheduler
from datetime import datetime
import os
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

statesData = {}
states = []

# git push heroku master
# heroku ps:scale web=1
# heroku logs --tail

def updateData():
    data = requests.get("https://covidtracking.com/api/states/daily").json()
    for dict in data:
        if dict['state'] not in states :
            states.append(dict['state'])
        if dict['state'] not in statesData:
            data = '"' + str(dict['state']) + '" :' + str({ dict['date']: dict['positive']})
            statesData[dict['state']] = {dict['date']: dict['positive']}
        elif dict['date'] not in statesData[dict['state']]:
            statesData[dict['state']][dict['date']] = dict['positive']

app.apscheduler.add_job(id="refresh", func=updateData, trigger='interval', hours=1)

updateData()

@app.route("/")
def index():
    return jsonify(statesData)

@app.route("/states")
def returnStates():
    return jsonify(states)

@app.route("/state/<string:state>")
def returnState(state):
    return jsonify(statesData[state.upper()])

# @app.route("/state/<string: state>")
# def state(state):
#     # return that states data

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)