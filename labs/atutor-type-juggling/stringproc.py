from bs4 import BeautifulSoup
import re

with open("out.txt", "r") as f:
	text = f.read()

id_list = re.findall(r'To set a new password.*id=\\\"(\d+)\\\"', text)
print(id_list)