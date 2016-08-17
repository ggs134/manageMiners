from flask import Flask
import paramikoWrapper as wrap
from flask import render_template


app = Flask(__name__)

@app.route('/log/<int:minerNum>')
def paramiko(minerNum):
	# return str(minerNum)

    if int(minerNum) < 9:
        client = wrap.SSHClient('goldrush2.hopto.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
        result = client.execute('tail -10 ethminer.err.log')['out']
        return render_template('testlayout.html', results=result)

    elif int(minerNum) in [7, 13, 37]:
        return "page does not exist"
		
    else:
        client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
        result = client.execute('tail -10 ethminer.err.log')['out']
	# result = str(result)
	return render_template('testlayout.html', results=result)

if __name__ == '__main__':
	app.run(debug=True)
