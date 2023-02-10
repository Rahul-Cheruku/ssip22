import json
import math

from flask import Flask, render_template

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime


# MONGODB
def sendittomongo(docs, UID):
    client = MongoClient("mongodb+srv://admin:admin@cluster0.wwafvh9.mongodb.net/?retryWrites=true&w=majority")
    db = client.node314
    ref = {"node1": db.node1, "node2": db.node2, "node3": db.node3, }
    collection = ref[f"{UID}"]
    docs['date&time'] = datetime.now().strftime("%d-%m-%Y %H:%M")
    docs['date'] = datetime.now().strftime("%d-%m-%Y")
    docs['hour'] = datetime.now().strftime("%H:%M")
    docs['seqno'] = nodedata[UID]['seqno']
    nodedata[UID]['seqno'] +=1
    collection.insert_one(docs)
    client.close()


def lastnentrieswithid(N, UID):
    client = MongoClient("mongodb+srv://admin:admin@cluster0.wwafvh9.mongodb.net/?retryWrites=true&w=majority")
    db = client.node314
    ref = {"node1": db.node1, "node2": db.node2, "node3": db.node3,"dummy": db.dummy }
    collection = ref[UID]
    client.close()
    if UID=="dummy":
        return [{'x':item["date"],'y':item['currentlevel']} for item in collection.find()][::-1][0:N]
    else:
        return [{'x': item["date&time"], 'y': item['currentlevel']} for item in collection.find()][::-1][0:N]

def allentries(UID):
    client = MongoClient("mongodb+srv://admin:admin@cluster0.wwafvh9.mongodb.net/?retryWrites=true&w=majority")
    db = client.node314
    ref = {"node1": db.node1, "node2": db.node2, "node3": db.node3,"dummy": db.dummy }
    collection = ref[UID]
    ayush = [{'x': item["date&time"], 'y': item['currentlevel']} for item in collection.find()][::-1]
    tanvi = [{'x':item["date"],'y':item['currentlevel']} for item in collection.find()][::-1]
    client.close()
    if UID=="dummy":
        return tanvi
    else:
        return ayush



def latestentry(UID):
    client = MongoClient("mongodb+srv://admin:admin@cluster0.wwafvh9.mongodb.net/?retryWrites=true&w=majority")
    db = client.node314
    ref = {"node1": db.node1, "node2": db.node2, "node3": db.node3,"dummy": db.dummy }
    collection = ref[UID]
    client.close()
    if UID=="dummy":
        return [{'x':item["date"],'y':item['currentlevel']} for item in collection.find()][::-1][0]
    else:
        return [{'x': item["date&time"], 'y': item['currentlevel']} for item in collection.find()][::-1][0]



nodedata = {
    'node1': {'id': 'Node-1', 'location': 'DGGEC-Surat', 'microcontroller': 'ESP32',
              'powersource': 'Battery + Solar Pannel', 'connectivity': 'Wifi-enabled','seqno':1 },
    'node2': {'id': 'Node-2', 'location': 'VNSGU-Surat', 'microcontroller': 'ESP32',
              'powersource': 'Battery + Solar Pannel', 'connectivity': 'Wifi-enabled','seqno':1},
    'node3': {'id': 'Node-3', 'location': 'SCET-Surat', 'microcontroller': 'ESP32',
              'powersource': 'Battery + Solar Pannel', 'connectivity': 'Wifi-enabled','seqno':1},
}

app = Flask(__name__)


@app.route("/")
def Hello_user():
    return render_template('index.html')


@app.route("/<nodex>")
def nodex(nodex):
    # x = UID
    x = str(nodex.split('.')[0])
    # N is no of entries per day
    N = 30
    le = allentries(x)

    x_values = []
    y_values = []
    for i in range(len(le)):
        x_values.append(le[i]['x'])
        y_values.append(le[i]['y'])
    maxi = y_values.index(max(y_values))
    mini = y_values.index(min(y_values))
    level_max = y_values[maxi]
    time_max = x_values[maxi]
    time_min = x_values[mini]
    level_min = y_values[mini]
    currentdata = {"24maxtime": time_max,"24maxlevel":level_max,"24mintime":time_min,"24minlevel":level_min,'currentlevel':le[0]['y'],'lastrecieved':le[0]['x']}
    return render_template('node-x.html', data=nodedata[x], current=currentdata, x_values1=json.dumps(x_values[0:N]), y_values1=json.dumps(y_values[0:N*7]), x_values2=json.dumps(x_values[0:N*7]), y_values2=json.dumps(y_values[0:N*7]),x_values3=json.dumps(x_values), y_values3=json.dumps(y_values))


@app.route("/currentstatus/<data>")
def Guess(data):
    li = list(data.split('_'))
    docs = {li[0]: li[1], li[2]: li[3]}
    sendittomongo(docs, li[1])
    # pattern: uniqueid_id_currentlevel_lvl
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == "__main__":
    app.run(debug=True)
