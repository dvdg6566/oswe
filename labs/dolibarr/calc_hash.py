import hashlib, string, itertools

A = 0

for length in range(1, 7):
	for word in map(''.join,itertools.product(string.ascii_lowercase, \
		repeat=int(length))):

		A += 1
		h = hashlib.md5(word.encode()).hexdigest()
		
		h = ''.join(filter(lambda x:not x.isdigit(), h))
		print(h)
		if 'exec' in h:
			print(word)
			print(h)
			exit(0)

print(A)