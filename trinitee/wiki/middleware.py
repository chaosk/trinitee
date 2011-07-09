import re
from django.http import HttpResponseRedirect


class WikiWhitespaceMiddleware(object):
	"""
	Turns all whitespace characters in request path to underscores.
	"""

	def process_request(self, request):
		if not request.path.startswith('/wiki/'):
			return
		r = re.compile(r'\s+')
		if r.search(request.path):
			return HttpResponseRedirect(r.sub('_', request.path))

