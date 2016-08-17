#-*- coding: utf-8 -*-

from flask import Flask
import paramikoWrapper as wrap
from flask import render_template


app = Flask(__name__)

@app.route('/')
def paramiko():
	client = wrap.SSHClient('goldrush.iptime.org', 50023, 'miner23', 'rlagnlrud' )
	# 리스트 타입 result
	result = client.execute('tail -10 ethminer.err.log')['out']

	# 리스트 타입 result -> 딕셔너리타입으로 바꾸기
	result = [{result.index(i): i } for i in result]

	return render_template('testlayout.html', results=result)


if __name__ == '__main__':
	app.run(debug=True)
