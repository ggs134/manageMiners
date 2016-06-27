import requests
# import time
import datetime

def getMinedEther():
    res = requests.get("http://ethereum.miningpoolhub.com/index.php?page=api&action=getusertransactions&api_key=a8c9f5ea1a4045f6809c9a47c4746f5ae4aa5e136bf96ec0ce4223734c96a128")
    # res.json()
    data = res.json()['getusertransactions']['data']['transactions']

    credits = []
    fee = []

    for i in range(len(data)):
        transaction = data[i]
        trTime = datetime.datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
        # print 1,trTime
        # print 2,datetime.datetime.now()
        # print 3,datetime.timedelta(days=1)
        print "TRTIME", trTime
        print "UTC" ,datetime.datetime.utcnow()
        print "diff", datetime.datetime.utcnow() - trTime > datetime.timedelta(hours=3), datetime.datetime.utcnow() - trTime
        if transaction["type"] == "Fee":
            fee.append(data[i]['amount'])
        elif transaction["type"] == "Credit":
            credits.append(data[i]['amount'])
        elif datetime.datetime.utcnow() - trTime > datetime.timedelta(days=1):
            # print datetime.datetime.utcnow()
            break


    netValue = sum(credits) - sum(fee)
    print sum(credits)
    return netValue
    # print "credits", sum(credits)
    # print "fee", sum(fee)
    # print "net", sum(credits) - sum(fee)
    # print "percent" ,sum(fee)/ sum(credits) * 100


if __name__ == "__main__":
    getMinedEther()
