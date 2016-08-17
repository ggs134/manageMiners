#-*- coding: utf-8 -*-

from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from threading import Thread
import time
import json
import requests
import get24mined
import paramikoWrapper as wrap

app = Flask(__name__)
socketio = SocketIO(app)
thread = None

miners_farm1 = [1,2,3,4,5,6,8,9,10,11,12]
miners_farm2 = [i for i in range(14,39) if i is not 37 ]
miner_list = miners_farm1 + miners_farm2


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
            count = 10;
            for i in range(self.interval):
                socketio.emit("timer status", {"data": count }, namespace="/jsh")
                time.sleep(1)
                count -=1



@app.route('/')
def index():
    minedEther = get24mined.getMinedEther()
    global thread
    if thread is None:
        thread = getMiningPoolHubData(10)
        thread.daemon = True
        thread.start()
    return render_template('main3.htm', machines=miner_list, lastMined=minedEther)

@app.route('/log')
def log():
    return render_template('log.html', machines=miner_list)

@app.route('/log/<int:minerNum>')
def paramiko(minerNum):
    if minerNum in [2, 9, 7, 13, 37]:
        result = ["LOG does not exist"]
        return render_template('log.html', machines=miner_list, results=result)

    elif (minerNum < 9) or (minerNum == 14) :
        client = wrap.SSHClient('goldrush2.hopto.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
        result = client.execute('tail -10 ethminer.err.log')['out']
        return render_template('log.html', machines=miner_list, results=result)

    elif minerNum in [10,11,12]:
        portMapping = {10:22, 11:443, 12:444}
        client = wrap.SSHClient('ggs134.gonetis.com', portMapping[int(minerNum)], 'miner'+str(minerNum), 'rlagnlrud' )
        result = client.execute('tail -10 ethminer.err.log')['out']
        return render_template('log.html', machines=miner_list, results=result)

    else:
        client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
        result = client.execute('tail -10 ethminer.err.log')['out']
        return render_template('log.html', machines=miner_list, results=result)


if __name__ == '__main__':
    socketio.run(app , debug=True, host='0.0.0.0')
