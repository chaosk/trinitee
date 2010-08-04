""" Author: Robert Chmielowiec <http://chmielowiec.net> """

def check_ips(pattern, string):
	ips = zip(pattern.split('.'), string.split('.'))
	for c, (i, j) in enumerate(ips):
		if i == j or i == '*':
			continue
		elif '-' in i:
			start, end = i.split('-')
			a, start, end = map(int, (j, start, end))
			if a < start or a > end:
				return False
		else:
			return False
	return True


def check_pattern(pattern):
	pattern = pattern.split('.')

	if len(pattern) != 4:
		return False

	for c, i in enumerate(pattern):
		if not i:
			return False
		if i == '*':
			continue
		elif i.isdigit():
			if int(i) < 0 and int(i) > 255:
				return False
		elif '-' in i:
			r = i.split('-')
			if len(r) != 2 or "" in r:
				return False
		else:
			return False
	return True
