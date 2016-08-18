#-*- coding: utf-8 -*-

from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from threading import Thread
import time
import json
import requests
import get24mined
import paramikoWrapper as wrap
import re
import pymongo

app = Flask(__name__)
socketio = SocketIO(app)
thread = None
thread2 = None

miners_farm1 = [1,2,3,4,5,6,8,14]
miners_farm2 = [9,10,11,12]
miners_farm3 = [i for i in range(15,39) if i is not 37 ]
miner_list = miners_farm1 + miners_farm2 + miners_farm3

mongoClient = pymongo.MongoClient("52.78.47.231",27017, connect=False)
mongoDB = mongoClient.di


global threads

class getMiningPoolHubData(Thread):
    def __init__(self, interval):
        super(getMiningPoolHubData,self).__init__()
        self.interval = interval

    def run(self):
        while True:
            response = requests.get("http://ethereum.miningpoolhub.com/index.php?page=api&action=getuserworkers&api_key=a8c9f5ea1a4045f6809c9a47c4746f5ae4aa5e136bf96ec0ce4223734c96a128")
            response2 = requests.get("http://ethereum-classic.miningpoolhub.com/index.php?page=api&action=getuserworkers&api_key=a8c9f5ea1a4045f6809c9a47c4746f5ae4aa5e136bf96ec0ce4223734c96a128")
            json_response = response.json()
            json_response2 = response2.json()
            data = json_response["getuserworkers"]["data"]
            data2 = json_response2["getuserworkers"]["data"]
            # print data
            socketio.emit("miningpoolhub status", {"data": data, "data2":data2}, namespace="/jsh")
            count = self.interval
            for i in range(self.interval):
                socketio.emit("timer status", {"data": count}, namespace="/jsh")
                time.sleep(1)
                count -=1

class getMongoDBData(Thread):
    def __init__(self, interval):
        super(getMongoDBData, self).__init__()
        self.interval = interval
    def run(self):
        while True:
            print "thread2 started"
            data = []
            # targetData = {"hashrate":1, "hashrateC":1, "gpuTemprature":1, "fanspeed":1}
            for i in miners_farm1:
                print i
                try:
                    res = mongoDB["miner"+str(i)].find(sort=[("_id",-1)]).limit(1).next()
                    # print res
                    # print res["hashrate"]
                    rs = {"hash":res["hashrate"]+res["hashrateC"], "temp":res["gpuTemprature"], "fanspeed":res["fanspeed"]}
                    print rs
                    print "hi"+str(i)
                    data.append(rs)
                    # print rs
                except Exception as e:
                    print # coding=utf-8
            print data
            socketio.emit("mongoDB data", {"data":data}, namespace="/jsh")
            count2 = self.interval
            for i in range(self.interval):
                socketio.emit("mongo timer status", {"data": count2}, namespace="/jsh")
                time.sleep(1)
                count2 -= 1

@socketio.on('message', namespace='/reset')
def handle_message(message):
    number = int(message["data"][6:])
    dNP = getDomainAndPort(number)
    try:
        # print "socket!"
        client = wrap.SSHClient(dNP["domain"], dNP["port"], 'miner'+str(number), 'rlagnlrud' )
        # out = client.execute('tail -10 ethminer.err.log')['out']
        client.execute("sudo reboot")["out"]
        socketio.emit("reboot result",{"data": "마이너"+str(number)+" 재부팅중.. "} ,namespace="/reset")
    except Exception as e:
        # print e
        message = "마이너"+str(number)+" 재부팅 실패  "+str(e)
        socketio.emit("reboot result",{"data": message} ,namespace="/reset")

@app.route('/')
def index():
    minedETH = get24mined.getMinedEther()
    minedETC = get24mined.getMinedEtc()
    prices = get24mined.priceTicker()
    global thread
    if thread is None:
        thread = getMiningPoolHubData(10)
        thread.daemon = True
        thread.start()
    return render_template('main3.htm', machines=miner_list, lastMinedETH=minedETH, lastMinedETC=minedETC, prices=prices)

@app.route('/status')
def status():
    # global thread2
    # if thread2 is None:
    #     print "hi"
    #     thread2 = getMongoDBData(60)
    #     thread2.daemon = True
    #     thread2.start()
    data1 = []
    data2 = []
    for i in miners_farm1:
        try:
            res = mongoDB["miner"+str(i)].find(sort=[("_id",-1)]).limit(1).next()
            # print res
            # print res["hashrate"]
            # rs = {"hash":res["hashrate"]+res["hashrateC"], "temp":res["gpuTemprature"], "fanspeed":res["fanspeed"]}
            # print res
            temp = [int(j) for j in res["gpuTemperature"].strip("[]").split(",")]
            averageTemp = sum(temp) / float(len(temp))
            rs = {"username": res["username"], "hash":(res["hashrate"]+res["hashrateC"])/1000.0, "temp":temp, "average_temp": averageTemp, "gpu_num":len(temp)}
            # print rs
            data1.append(rs)
        except Exception as e:
            print e

    for i in miners_farm3:
        try:
            res = mongoDB["miner"+str(i)].find(sort=[("_id",-1)]).limit(1).next()
            # print res
            # print res["hashrate"]
            # rs = {"hash":res["hashrate"]+res["hashrateC"], "temp":res["gpuTemprature"], "fanspeed":res["fanspeed"]}
            # print res
            temp = [int(j) for j in res["gpuTemperature"].strip("[]").split(",")]
            averageTemp = sum(temp) / float(len(temp))
            rs = {"username": res["username"], "hash":(res["hashrate"]+res["hashrateC"])/1000.0, "temp":temp, "average_temp": averageTemp, "gpu_num":len(temp)}
            # print rs
            data2.append(rs)
        except Exception as e:
            print e

    total_data = data1 + data2
    average_list1 = [i["average_temp"] for i in data1 ]
    average_list2 = [ i["average_temp"] for i in data2 ]
    total_average_list = average_list1 + average_list2
    total_average = sum(total_average_list) / float(len(total_average_list))
    average1 = sum(average_list1) / float(len(average_list1))
    average2 = sum(average_list2) / float(len(average_list2))

    max_temp = max(max([i["temp"] for i in total_data]))
    max_list = [i["username"] for i in total_data if max_temp in i["temp"]]
    # print total_data
    # print total_data[0]["gpu_num"]
    total_gpu_num = sum([int(i["gpu_num"]) for i in total_data])
    hash_per_gpu = sum([int(i["hash"]) for i in total_data]) / float(total_gpu_num)

    #profit related info
    minedETH = get24mined.getMinedEther()
    minedETC = get24mined.getMinedEtc()
    prices = get24mined.priceTicker()

    #weather realted info
    weather = get24mined.getWeatherInfo()

    profit = {"ETH_price": prices["eth"], "ETC_price":prices["etc"], "BTC_price":prices["btc"],\
    "ETH24": minedETH*prices["eth"]*12,"ETC24":minedETC*prices["etc"]*24}

    statistics = {"total_average":total_average, "average1":average1, "average2":average2, \
    "max_list":max_list , "max_temp": max_temp, "total_gpu_num":total_gpu_num, "hash_per_gpu": hash_per_gpu}

    # print data
    return render_template('status.html', statusData1=data1, statusData2=data2, \
    weather=weather, statistics=statistics, profit=profit)

@app.route('/log')
def log():
    return render_template('log.html', machines=miner_list)

@app.route('/log/<int:minerNum>')
def paramiko(minerNum):

    dNP = getDomainAndPort(minerNum)
    # print dNP
    try:
        client = wrap.SSHClient(dNP["domain"], dNP["port"], 'miner'+str(minerNum), 'rlagnlrud' )
        result = client.execute('tail -10 ethminer.err.log')['out']
        result = convert_list(result)
        return render_template('log.html', machines=miner_list, results=result, targetNum = minerNum)
    except Exception as e:
        print e
        result = ["LOG does not exist or Connection Error", str(e)]
        return render_template('log.html', machines=miner_list, results=result, targetNum = minerNum)

    # if minerNum in [2, 9, 7, 13, 37]:
    #     result = ["LOG does not exist"]
    #     return render_template('log.html', machines=miner_list, results=result, targetNum = minerNum)
    #
    # elif (minerNum < 9) or (minerNum == 14) :
    #     client = wrap.SSHClient('goldrush2.hopto.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
    #     result = client.execute('tail -10 ethminer.err.log')['out']
    #     result = convert_list(result)
    #     return render_template('log.html', machines=miner_list, results=result, targetNum = minerNum)
    #
    # elif minerNum in [10,11,12]:
    #     portMapping = {10:22, 11:443, 12:444}
    #     client = wrap.SSHClient('ggs134.gonetis.com', portMapping[int(minerNum)], 'miner'+str(minerNum), 'rlagnlrud' )
    #     result = client.execute('tail -10 ethminer.err.log')['out']
    #     result = convert_list(result)
    #     return render_template('log.html', machines=miner_list, results=result, targetNum = minerNum)
    #
    # else:
    #     client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
    #     result = client.execute('tail -10 ethminer.err.log')['out']
    #     result = convert_list(result)
    #     return render_template('log.html', machines=miner_list, results=result, targetNum = minerNum)

def getDomainAndPort(minerNumber):
    if minerNumber in [2, 9, 7, 13, 37]:
        return {"domain":"Does not exists","port":"Does not exists"}
    elif (minerNumber < 9) or (minerNumber == 14):
        return {"domain": "goldrush2.hopto.org", "port":50000+int(minerNumber)}
    elif minerNumber in [10,11,12]:
        portMapping = {10:22, 11:443, 12:444}
        return {"domain": "ggs134.gonetis.com", "port": portMapping[minerNumber]}
    else:
        return {"domain":"goldrush.iptime.org", "port":50000+int(minerNumber)}

def convert_list(lst):
    newLst = [i.encode("utf-8").replace("[","") for i in lst]
    return [re.sub(r"\d{2}m|\d{1}m","",j).decode("utf-8") for j in newLst ]



if __name__ == '__main__':
    socketio.run(app , debug=True, host='0.0.0.0')
