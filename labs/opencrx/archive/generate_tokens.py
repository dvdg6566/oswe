class JavaRandom():
	"""docstring for JavaRandom"""
	def __init__(self, seed):
		self.seed = (seed ^ 25214903917) & ((1<<48) -1)
		
	def next(self, bits):
		# print((self.seed * 25214903917 + 11))
		self.seed = (self.seed * 25214903917 + 11) & ((1<<48) -1)
		# print(self.seed)
		return int(self.seed >> (48 - bits))

	# Returns value from [0,n)
	def nextInt(self, n):
		if (n<=0):
			exit(0)
		
		bits = 0
		val = 0
		while True:
			bits = self.next(31)
			val = bits % n
			if (bits - val + (n-1) >= 0): 
				return val

	def generate_token(self, length):
		alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
		s = ""
		for i in range(length):
			x = self.nextInt(62)
			s += alphabet[x]
		return s

def generate_tokens(low, high):
	length = 40
	for i in range(low, high):
		rand = JavaRandom(i)
		print(rand.generate_token(length))

if __name__ == '__main__':
	generate_tokens(100, 150)