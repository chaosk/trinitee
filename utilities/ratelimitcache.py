from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.cache import cache
from datetime import datetime, timedelta
import functools
import hashlib

"""
ratelimitcache for Django
=========================
By Simon Willison - http://simonwillison.net/
"""


class ratelimit(object):
	"Instances of this class can be used as decorators"
	# This class is designed to be sub-classed
	minutes = 2 # The time period
	requests = 20 # Number of allowed requests in that time period
	name = ''

	prefix = 'rl-' # Prefix for memcache key

	def __init__(self, **options):
		for key, value in options.items():
			setattr(self, key, value)

	def __call__(self, fn):

		def wrapper(request, *args, **kwargs):
			return self.view_wrapper(request, fn, *args, **kwargs)
		functools.update_wrapper(wrapper, fn)
		return wrapper

	def view_wrapper(self, request, fn, *args, **kwargs):
		if not self.should_ratelimit(request):
			return fn(request, *args, **kwargs)

		counts = self.get_counters(request).values()

		# Increment rate limiting counter
		self.cache_incr(self.current_key(request))

		# Have they failed?
		if sum(counts) >= self.requests:
			return self.disallowed(request)

		return fn(request, *args, **kwargs)

	def cache_get_many(self, keys):
		return cache.get_many(keys)

	def cache_incr(self, key):
		# memcache is only backend that can increment atomically
		try:
			# add first, to ensure the key exists
			cache._cache.add(key, '0', time=self.expire_after())
			cache._cache.incr(key)
		except AttributeError:
			cache.set(key, cache.get(key, 0) + 1, self.expire_after())

	def should_ratelimit(self, request):
		return True

	def get_counters(self, request):
		return self.cache_get_many(self.keys_to_check(request))

	def keys_to_check(self, request):
		extra = self.key_extra(request)
		now = datetime.now()
		return [
			'%s%s-%s' % (
				self.prefix,
				extra,
				(now - timedelta(minutes = minute)).strftime('%Y%m%d%H%M'),
			) for minute in range(self.minutes + 1)
		]

	def current_key(self, request):
		return '%s%s-%s' % (
			self.prefix,
			self.key_extra(request),
			datetime.now().strftime('%Y%m%d%H%M'),
		)

	def key_extra(self, request):
		# By default, their IP address is used
		key = request.META.get('REMOTE_ADDR', '')
		if self.name:
			key += '-' + self.name
		return key

	def disallowed(self, request):
		"Over-ride this method if you want to log incidents"
		resp = render_to_response('420.html',
			context_instance=RequestContext(request))
		resp.status_code = 420
		return resp

	def expire_after(self):
		"Used for setting the memcached cache expiry"
		return (self.minutes + 1) * 60


class ratelimit_post(ratelimit):
	"Rate limit POSTs - can be used to protect a login form"
	key_field = None # If provided, this POST var will affect the rate limit

	def should_ratelimit(self, request):
		return request.method == 'POST'

	def key_extra(self, request):
		# IP address and key_field (if it is set)
		extra = super(ratelimit_post, self).key_extra(request)
		if self.key_field:
			value = hashlib.sha1(request.POST.get(self.key_field, '')).hexdigest()
			extra += '-' + value
		return extra


class ratelimit_post_manual(ratelimit_post):
	"Same as above, except that its not automatically incrementing counters"

	def view_wrapper(self, request, fn, *args, **kwargs):
		if not self.should_ratelimit(request):
			return fn(request, *args, **kwargs)

		counts = self.get_counters(request).values()

		# Have they failed?
		if sum(counts) >= self.requests:
			return self.disallowed(request)

		return fn(request, *args, **kwargs)


# It gets worse
# FIXME Needs a lot of care

class ratelimit_post_manual_modify_fn(ratelimit_post_manual):

	def view_wrapper(self, request, fn, *args, **kwargs):
		if not self.should_ratelimit(request):
			return fn(request, *args, **kwargs)

		counts = self.get_counters(request).values()

		# Have they failed?
		if sum(counts) >= self.requests:
			if self.punishment:
				kwargs['punishment'] = self.punishment
			else:
				return self.disallowed(request)

		return fn(request, *args, **kwargs)

	def add_punishment(self, punishment):
		self.punishment.append(punishment)

class ratelimit_post_manual_punish_recaptcha(ratelimit_post_manual_modify_fn):

	def view_wrapper(self, request, fn, *args, **kwargs):
		if not self.should_ratelimit(request):
			return fn(request, *args, **kwargs)

		counts = self.get_counters(request).values()

		# Have they failed?
		if sum(counts) >= self.requests:
			if not 'punishment' in kwargs:
				kwargs['punishment'] = []
			kwargs['punishment'].append('recaptcha')

		return fn(request, *args, **kwargs)

class ratelimit_post_manual_punish_sleep(ratelimit_post_manual_modify_fn):

	def view_wrapper(self, request, fn, *args, **kwargs):
		if not self.should_ratelimit(request):
			return fn(request, *args, **kwargs)

		counts = self.get_counters(request).values()

		# Have they failed?
		if sum(counts) >= self.requests:
			if not 'punishment' in kwargs:
				kwargs['punishment'] = []
			kwargs['punishment'].append('sleep')

		return fn(request, *args, **kwargs)


class ratelimit_post_manual_not_staff(ratelimit_post_manual):

	def should_ratelimit(self, request):
		return not (request.user.is_staff or request.user.is_superuser)