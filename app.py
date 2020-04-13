from flask import Flask, jsonify
import requests
from flask_apscheduler import APScheduler
from datetime import datetime, date, timedelta
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
# source env/bin/activate

def updateData():
    today = date.today()
    firstDay = date(2020, 3, 3)
    delta = today - firstDay
    days = delta.days
    data = requests.get("https://covidtracking.com/api/states/daily").json()
    for dict in data:
        if dict['state'] not in states :
            states.append(dict['state'])
        if dict['state'] not in statesData:
            empty = {}
            for x in range(days):
                past = datetime.now() - timedelta(x+1)
                year = str(past.year)
                month = str(past.month)
                day = str(past.day)
                if len(str(past.month)) == 1:
                    month = str(0) + month
                if len(str(past.day)) == 1:
                    day = str(0) + day
                pastStr = str(past.year) + month + day
                empty[pastStr] = 0
            
            statesData[dict['state']] = empty
        if int(dict['date']) >= 20200303:
            try:
                statesData[dict['state']][str(dict['date'])] = dict['positive']
            except:
                statesData[dict['state']][str(dict['date'])] = 0


def getTopTen():
    def getPos(res):
        if res['positive'] == None:
            return 0
        return res['positive']

    res = requests.get("https://covidtracking.com/api/states").json()
    res.sort(key=lambda x: getPos(x))
    last = res[(len(res) - 10):len(res)]
    res = {}
    for dict in last:
        res[dict['state']] = dict['positive']
    return res


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

@app.route("/topten")
def returnTopTen():
    return jsonify(getTopTen())

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)