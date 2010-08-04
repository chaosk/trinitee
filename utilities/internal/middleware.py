import datetime
import re
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render_to_response
from django.template import RequestContext
from accounts.models import UserProfile
from misc.models import Ban, StoredNotification
from utilities.annoying.functions import get_config
from utilities.internal.ip import check_ips

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


class MaintenanceModeMiddleware(object):
	def process_request(self, request):
		if not get_config('MAINTENANCE_MODE', False):
			return
		if request.path in ['/user/login/', '/user/logout/'] \
			or 'static' in request.path:
			return
		if hasattr(request, 'user') \
			and (request.user.is_staff or request.user.is_superuser):
			return
		resp = render_to_response('503.html',
			{'message': get_config('MAINTENANCE_MESSAGE', None)},
			context_instance=RequestContext(request))
		resp.status_code = 503
		return resp

	def process_view(self, request, view_func, *view_args, **view_kwargs):
		if not get_config('MAINTENANCE_MODE', False):
			return
		if 'static' in request.path or '__debug__' in request.path:
			return
		if hasattr(request, 'user') \
			and (request.user.is_staff or request.user.is_superuser):
			messages.warning(request, "Site is currently running under"
				" maintenance mode, please turn it off"
				" after finishing your work.")


class BanMiddleware(object):
	def process_view(self, request, view_func, *view_args, **view_kwargs):
		bans = cache.get('misc_bans')
		if hasattr(request, 'user') and (request.user.is_staff or request.user.is_superuser) \
			or request.path in ['/user/login/', '/user/logout/'] \
			or 'static' in request.path:
			return
		if bans is None:
			bans = Ban.objects. \
				exclude(expires_at__lte=datetime.today()). \
				values_list('banned_mask', 'banned_user', 'comment', 'expires_at')
			cache.set('misc_bans', bans)
		for ban in bans:
			if hasattr(request, 'user') and ban[1] == request.user.id \
				or check_ips(ban[0], request.META['REMOTE_ADDR']):
				resp = render_to_response('misc/banned.html',
					{'expires_at': ban[3], 'comment': ban[2]},
					context_instance=RequestContext(request))
				resp.status_code = 403
				return resp


class StoredNotificationsMiddleware(object):
	def process_request(self, request):
		if request.user.is_authenticated():
			notifications = StoredNotification.objects \
				.filter(user=request.user).distinct('message')
			for notification in notifications: 
				messages.add_message(request, notification.level, 
					notification.message) 
			if notifications: 
				StoredNotification.objects.filter(user=request.user).delete()
