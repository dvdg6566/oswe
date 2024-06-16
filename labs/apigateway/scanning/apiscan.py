import argparse
import json
import requests

from test_url import check_url

with open("params.txt", "r") as f:
	params = f.read().split('\n')

for word in params:
	url = f"http://172.16.16.5:9000/api/render{word}"
	print(url)

	res = check_url(url)
	if res:
		print(f"{word}\tOPEN")
	else:
		print(f"{word}\tCLOSED")

# with open("apiwordlist.txt", "r") as f:
# 	apiwords = f.read().split('\n')

# for word in apiwords:
# 	url = f"http://172.16.16.5:9000{word}"
# 	print(url)

# 	res = check_url(url)
# 	if res:
# 		print(f"{word}\tOPEN")
# 	else:
# 		print(f"{word}\tCLOSED")