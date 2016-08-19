import requests
import datetime

def getMinedEther():
    res = requests.get("http://ethereum.miningpoolhub.com/index.php?page=api&action=getusertransactions&api_key=a8c9f5ea1a4045f6809c9a47c4746f5ae4aa5e136bf96ec0ce4223734c96a128")
    data = res.json()['getusertransactions']['data']['transactions']
    credits = []
    fee = []

    for i in range(len(data)):
        transaction = data[i]
        trTime = datetime.datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
        if transaction["type"] == "Fee":
            fee.append(data[i]['amount'])
        elif transaction["type"] == "Credit":
            credits.append(data[i]['amount'])
        elif datetime.datetime.now() - trTime > datetime.timedelta(hours=-2):
            # print "hour2"
            # print trTime
            break

    netValue = sum(credits) - sum(fee)
    return netValue

def getMinedEtc():
    res = requests.get("http://ethereum-classic.miningpoolhub.com/index.php?page=api&action=getusertransactions&api_key=a8c9f5ea1a4045f6809c9a47c4746f5ae4aa5e136bf96ec0ce4223734c96a128")
    data = res.json()['getusertransactions']['data']['transactions']
    credits = []
    fee = []

    for i in range(len(data)):
        transaction = data[i]
        trTime = datetime.datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
        # print trTime
        # print "between : "+repr(datetime.datetime.utcnow() - trTime)
        # print datetime.timedelta(hours=1)
        # print trTime
        if transaction["type"] == "Fee":
            fee.append(data[i]['amount'])
        elif transaction["type"] == "Credit":
            credits.append(data[i]['amount'])
        elif datetime.datetime.now() - trTime > datetime.timedelta(hours=-1):
            # print "hour2"
            # print trTime
            break

    netValue = sum(credits) - sum(fee)
    return netValue

def getWeatherInfo():
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather?id=1832743&appid=b2dcc9662a3eaa79a24a78b3d2767b96")
        temp = res.json()["main"]["temp"]-273
        hum = res.json()["main"]["humidity"]
        return {"temp":temp, "humidity":hum}
    except Exception as e:
        return {"temp":0, "humidity":0}

def priceTicker():
    btc = requests.get("https://api.coinone.co.kr/ticker/?type=btc").json()["last"]
    etc = requests.get("https://api.coinone.co.kr/ticker/?type=etc").json()["last"]
    eth = requests.get("https://api.coinone.co.kr/ticker/?type=eth").json()["last"]
    return {"btc":int(btc),"eth":int(eth),"etc":int(etc)}

if __name__ == "__main__":
    # getMinedEther()
    # getWeatherInfo()
    priceTicker()
