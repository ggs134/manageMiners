from flask import Flask
import paramikoWrapper as wrap
from flask import render_template


app = Flask(__name__)

@app.route('/')
def paramiko():
	client = wrap.SSHClient('goldrush.iptime.org', 50023, 'miner23', 'rlagnlrud' )
	result = client.execute('tail -10 ethminer.err.log')['out']
	# result = str(result)
	return render_template('testlayout.html', results=result)

if __name__ == '__main__':
	app.run()
