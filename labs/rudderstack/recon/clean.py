import re

with open("routes.txt", "r") as f:
	text = f.read()

routes = re.findall(r'"(.*?/v1/.*?)"', text)
routes = list(set(routes))
routes.sort()

for i in routes: print(i)

with open("routes_clean.txt", "w") as f:
	f.write(('\n'.join(routes)))