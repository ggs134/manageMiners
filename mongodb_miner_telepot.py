# -*-coding:utf-8-*-

import pymongo
import time
import paramikoWrapper as wrap
import telepot
import re
import copy
import pprint

miners_farm1 = [1,2,3,4,5,6,8,14]
miners_farm2 = [9,10,11,12]
miners_farm3 = [i for i in range(15,39) if i is not 37 ]
#2,9윈도우, 7,13,37없음
miner_list = miners_farm1 + miners_farm2 + miners_farm3
cp_miner_list = copy.deepcopy(miner_list)

mongoClient = pymongo.MongoClient("52.78.93.195", 27017)
mongoDB = mongoClient.di

# tokenlist = ["254864168:AAHq16HhIx5J0jrySsN8nzNYliQOtZejBXk"]
idlist = [161289242]
bot = telepot.Bot("254864168:AAHq16HhIx5J0jrySsN8nzNYliQOtZejBXk")


# DB에서 데이터 받아서 20초 마다 ‘0’해시 확인
def checkHash():
    while True:
        # print '1) cp_miner_list', cp_miner_list
        if set(miner_list) == set(cp_miner_list):
            mlist = miner_list
        else:
            # print '2) cp_miner_list', cp_miner_list
            mlist = cp_miner_list

        print 'mlist', mlist

        for i in mlist:
            # print mongoDB["miner"+str(i)].find(sort=[("_id",-1)]).limit(1).next()
            try:
                res= mongoDB["miner"+str(i)].find(sort=[("_id",-1)]).limit(1).next()
                totalhash = res["hashrate"]+res["hashrateC"]
                print i, totalhash

                if totalhash == 0:
                    # mess = " Warning: the miner %s hashrate is '0' " % str(i)
                    # sendMessage(mess)

                    # 그리고 ssh 접속 후, 해시는 0인데 로그는 정상인 경우를 제외시키기 위해 로그 확인
                    try:
                        # for j in paramiko(i):
                        #     print "j", j
                        #     logToStr = " ".join(j)


                        # print "paramiko(i)", paramiko(i)
                        logToStr = " ".join(paramiko(i))
                        logToStr = logToStr.encode('utf-8')
                        # print "logToStr: ", type(logToStr)
                        # print logToStr

                        if bool(re.search('MH/s', logToStr)) == None:
                            mess = " Warning: the miner %s hashrate is '0' " % str(i)
                            sendMessageToidList(mess)
                        else:
                            print 'miner %s is operating..' % str(i)
                            pass
                    except Exception as e:
                        print e

                else:
                    pass

            except Exception as e:
                print e
        time.sleep(20)

def sendMessageToidList(message):
    # bot = telepot.Bot("254864168:AAHq16HhIx5J0jrySsN8nzNYliQOtZejBXk")
    # bot.sendMessage(161289242, message)
    for id in idlist:
        bot.sendMessage(id, message)

    # for i in token(tokenlist):
    #     for j in idlist:
    #         i.sendMessage(j, message)

# def token(tokenlist):
#     bot_list = []
#     for t in tokenlist:
#         bot_list.append(telepot.Bot(t))
#     return result


def paramiko(minerNum):
    result = ""
    if minerNum in [2, 9, 7, 13, 37]:
        result = "LOG does not exist"

    # elif (minerNum < 9) or (minerNum == 14) :
    elif (minerNum < 9):
        client = wrap.SSHClient('goldrush2.hopto.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
        result = client.execute('tail -10 ethminer.err.log')['out']

    elif minerNum in [10,11,12,14]:
        portMapping = {10:22, 11:443, 12:444, 14:21}
        client = wrap.SSHClient('ggs134.gonetis.com', portMapping[int(minerNum)], 'miner'+str(minerNum), 'rlagnlrud' )
        result = client.execute('tail -10 ethminer.err.log')['out']

    else:
        client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
        result = client.execute('tail -10 ethminer.err.log')['out']

    return result

# def recmessage(tokenlist):
#     result=[]
#     for i in token(tokenlist):
#         for j in i:
#             result.append(j.getUpdates()[-1]['message']['text'])



# 텔레그램에 로그 확인 log(숫자) 메세지 보내면 텔레그램에서 로그 보여줌
def recieveMessage(id, msg):
    # while 1:
        # response = bot.getUpdates()
    res = msg['text']

    if bool(re.search('log\(*', res)) == True:
        # type(res) is list
        res = re.findall(r"[0-9]+",res)
        # type(res[0]) is string
        minerNum = res[0]
        # type(minerNum) is string
        result = paramiko(minerNum)
        # type(result) is list
        # sendMessage(result)
        bot.sendMessage(id, result)
    elif bool(re.search('turnoff\(*', res)) == True:
        res = re.findall(r"[0-9]+",res)
        minerNum = res[0]
        # print minerNum
        cp_miner_list.remove(int(minerNum))
        # sendMessage('TurnOff miner%s' % minerNum)
        bot.sendMessage(id, 'yes, turnoff miner%s' % minerNum)

    elif bool(re.search('turnon\(*', res)) == True:
        res = re.findall(r"[0-9]+",res)
        minerNum = res[0]
        cp_miner_list.append(int(minerNum))
        # sendMessage('TurnOn miner%s' % minerNum)
        bot.sendMessage(id, 'yes, turnon miner%s' % minerNum)

    else:
        pass
    # time.sleep(20)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    # print content_type, chat_type, chat_id
    if content_type == 'text':
        # pprint.pprint(msg)
        recieveMessage(chat_id, msg)


# def fromid(idlist):
#     fromid_list = []
#     for f in idlist:
#         fromid_list.append()

if __name__ == '__main__':
    # checkHash()
    # recieveMessage()
    # print "hello"
    bot.message_loop(handle)
    print "listening.."
    # while 1:
    #     time.sleep(10)
    checkHash()
