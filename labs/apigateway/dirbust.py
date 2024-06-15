import argparse
import requests


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-a','--actionlist', help='actionlist to use')
	parser.add_argument('-t','--target', help='host/ip to target', required=True)
	parser.add_argument('-w','--wordlist', help='wordlist to use')
	args = parser.parse_args()
	target = args.target

	with open(args.actionlist, "r") as f:
		actions = f.read().split('\n')

	with open(args.wordlist, "r") as f:
		words = f.read().split('\n')

	print(len(words))
	print(len(actions))
	words = words[:2]

	results = []
	for word in words:
		print("Trying:", word)
		for action in actions:
			# print(action)
			url = f"{target}{word}/{action}"

			r_get = requests.get(url).status_code
			r_post = requests.post(url).status_code
			# print(url, r_get, r_post)

			if (r_get not in [204,401,403,404]):
				print("Discoverd:",url)
				print("GET Request Value:", r_get)
				results.append(url)

			if (r_post not in [204,401,403,404]):
				print("Discoverd:",url)
				print("POST Request Value:", r_post)
				results.append(url)

	print(results)

if __name__ == '__main__':
	main()