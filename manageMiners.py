from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

from threading import Thread
import time

import command_one as sshCommand
import manager

# from gevent import monkey
#
# monkey.patch_all()

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread=None

miners_farm1 = [1,3,4,5,6,7,8]
miners_farm2 = [i for i in range(14,39) if i is not 26 ]
miners_all = miners_farm1 + miners_farm2
ip_end_num = {1:39,3:36,4:35,5:38,6:37,7:31,8:33,14:40,15:3,16:7,17:8,
18:9,19:11,20:12,21:34,22:10,23:21,24:14,25:15,26:19,27:18,28:17,
29:16,30:20,31:26,32:29,33:25,34:23,35:24,36:28,37:22,38:27}

ip_end_num_test = {1:39,3:36}

# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         time.sleep(2)
#         count += 1
#         print count
#         res = manager.get_status("192.168.0.39",161)
#         # stdout = sshCommand.command_one(1, "tail -1 ethminer.err.log")[0]
#         # socketio.emit('my status', {'data': res, 'count': count}, namespace="/jsh")
#         print res[1]


class ReadTemperature(Thread):
    def __init__(self, num, interval):
        super(ReadTemperature, self).__init__()
        self.num = num
        self.interval = interval

    def run(self):
        while True:
            try:
                res = manager.get_status("192.168.0."+str(ip_end_num[self.num]), 161)
                print self.num, str(res[1]), type(res[1])
                socketio.emit('gpu status', {"cardNum":self.num,'temp':res[1], 'hash':res[0]}, namespace="/jsh")
                time.sleep(self.interval)
            except:
                print self.num, "error connection"
                socketio.emit('gpu status', {"cardNum":self.num,'temp':[None,None,None,None,None,None], "hash":None}, namespace="/jsh")
                time.sleep(self.interval)

            # print self.num, str(res[1]), type(res[1])
            # socketio.emit('gpu status', {"cardNum":self.num,'temp':res[1]}, namespace="/jsh")
            # time.sleep(self.interval)


@app.route('/')
def index():
    global threads
    if threads is None:
        threads = {}
        for num in ip_end_num:
            threads[num] = ReadTemperature(num,2)
        # if thread is None:
            # thread = Thread(target=background_thread)
            # thread = ReadTemperature(1,2)
            threads[num].daemon = True
            threads[num].start()
        return render_template('main2.htm', machines=ip_end_num)
    else:
        return render_template('main2.html', machines=ip_end_num)

# @app.route('/miners/<number>'):
# def get_log(number):
    


# @socketio.on('connect',namespace='/jsh')
# def test_connect():
#     emit('my response', {'data': 'Connected', 'count': 0})
#
# @socketio.on('my event',namespace='/jsh')
# def test_connect(message):
#     emit('my response', {'data': message["data"], 'count':0})

# @socketio.on('gpu status', namespace='/jsh')
# def test_message(message):
#     # session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('gpu status',{'data': message['temp']})


if __name__ == '__main__':
    socketio.run(app , debug=True, host='0.0.0.0')
