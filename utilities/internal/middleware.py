from accounts.models import UserProfile
from datetime import datetime
from django.conf import settings
import re

compiledLists = {}

"""
http://magicpc.wordpress.com/2009/09/22/get-online-users-in-django/
"""
class LastActivityMiddleware(object):
	def process_request(self, request):
		if not request.user.is_authenticated():
			return
		urlsModule = __import__(settings.ROOT_URLCONF, {}, {}, [''])
		skipList = getattr(urlsModule, 'skip_last_activity_date', None)
		skippedPath = request.path
		if skippedPath.startswith('/'):
			skippedPath = skippedPath[1:]
		if skipList is not None:
			for expression in skipList:
				compiledVersion = None
				if not compiledLists.has_key(expression):
					compiledLists[expression] = re.compile(expression)
				compiledVersion = compiledLists[expression]
				if compiledVersion.search(skippedPath):
					return
		profile = request.user.profile
		profile.last_activity_at = datetime.now()
		profile.last_activity_ip = request.META['REMOTE_ADDR']
		profile.save()
