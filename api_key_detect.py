import sys, os, re, itertools

ignored = ['.git', 'node_modules', 'bower_components', '.sass-cache', '.png', '.ico', \
            '.mov', '.pdf', '.bmp', '.wsdl', '.jar', '.json', '.exe', '.csv', '.jzb', \
            '.gz', '.zip', '.tar', '.o', '.so', '.a', '.xml', '.dll', '.msi', '.key', '.crt' ]

api_key_min_entropy_ratio = 0.5
api_key_min_length = 15

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def token_is_api_key(token):
	"""
	Returns True if the token is an API key or password.
	"""
	if len(token) < api_key_min_length:
		return (False, '')
	entropy = 0
	for a, b in pairwise(list(token)):
		if not ((str.islower(a) and str.islower(b)) or (str.isupper(a) and\
			str.isupper(b)) or (str.isdigit(a) and str.isdigit(b))):
			entropy += 1
	return (float(entropy) / len(token) > api_key_min_entropy_ratio, float(entropy) / len(token))

def line_contains_api_key(line):
	"""
	Returns True if any token in the line contains an API key or password.
	"""
	lline = line.lower()
	if not (lline.find("token") != -1 or \
	  lline.find("secret") != -1 or \
	  lline.find("key") != -1):
		return (False, '', '')

	tokens = re.findall(r"[\w]+", line)
	i = 0
	for token in tokens:
		result = token_is_api_key(token)
		if result[0]:
			ndx =  i - 3
			if ndx < 0:
				ndx = 0
			snippet = ' '.join(tokens[ndx: i+1])
			return (True, snippet, result[1])
			#return (True, token, result[1])
		i += 1
	return (False, '', '')

def scan_file(path_to_file):
	"""
	Prints out lines in the specified file that probably contain an API key or
	password.
	"""
	f = open(path_to_file)
	number = 1
	for line in f:
		result = line_contains_api_key(line)
		if result[0]:
			print '\033[1m' + path_to_file + ' : Line ' + str(number) + ' : Entropy ' + str(result[2]) + '\033[0m'
			print result[1]
			#print line
		number += 1

def scan_dir(path):
	"""
	Recursively walks through the specified directory and scans each file.
	Ignores hidden files and files matching the ignore list.
	"""
	for dirpath, _, filenames in os.walk(path):
		for name in filenames:
			if name[0] == '.':
				# ignore hidden files
				continue
			fullpath = os.path.join(dirpath, name)
			skip = False
			for ignore in ignored:
				if ignore in fullpath:
					skip = True
			if not skip:
				try:
					scan_file(fullpath)
				except:
					pass

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print 'Please specify path.'
		sys.exit(0)

	path = str(sys.argv[1])
	print 'Scanning directory: ' + path
	print 'Ignoring: ' + str(ignored)
	print 'For tokens with minimum entropy ratio: ' + str(api_key_min_entropy_ratio)

	scan_dir(path)
	
