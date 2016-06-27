from threading import Thread
import command_one
import sys
import time
from datetime import datetime
import requests

class getMiningPoolHubData(Thread):
    def __init__(self, interval):
        super(getMiningPoolHubData,self).__init__()
        self.interval = interval

    def run(self):
        while True:
            response = requests.get("http://ethereum.miningpoolhub.com/index.php?page=api&action=getuserworkers&api_key=a8c9f5ea1a4045f6809c9a47c4746f5ae4aa5e136bf96ec0ce4223734c96a128")
            json_response = response.json()
            data = json_response["getuserworkers"]["data"]

            for i in data:
                miner_num = int(i["username"][13:])
                if i["hashrate"] == 0:
                    try:
                        command_one.command_one(miner_num, "sudo reboot")
                        sys.stderr.write(str(datetime.now())+" miner"+str(miner_num)+" rebooting\n")
                    except:
                        sys.stderr.write(str(datetime.now())+" "+str(miner_num)+" Error Occured\n")
                        pass
                else:
                     sys.stderr.write(str(datetime.now())+" miner"+str(miner_num)+" No problem\n")

            # print data
            # socketio.emit("miningpoolhub status", {"data": data}, namespace="/jsh")
            time.sleep(self.interval)

if __name__ == "__main__":
    thread = getMiningPoolHubData(600)
    thread.start()
