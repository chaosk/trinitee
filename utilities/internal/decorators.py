import base64
from urllib import quote
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext


def user_passes_test_or_403(test_func, login_url=None):
	"""
	Decorator for views that checks that the user passes the given test.

	Anonymous users will be redirected to login_url, while users that fail
	the test will be given a 403 error.
	"""
	if not login_url:
		from django.conf import settings
		login_url = settings.LOGIN_URL

	def _dec(view_func):

		def _checklogin(request, *args, **kwargs):
			if test_func(request.user):
				return view_func(request, *args, **kwargs)
			elif not request.user.is_authenticated():
				return HttpResponseRedirect('%s?%s=%s' % (login_url,
					REDIRECT_FIELD_NAME, quote(request.get_full_path())))
			else:
				resp = render_to_response('403.html',
					context_instance=RequestContext(request))
				resp.status_code = 403
				return resp
		_checklogin.__doc__ = view_func.__doc__
		_checklogin.__dict__ = view_func.__dict__
		return _checklogin
	return _dec


def has_perm_or_403(perm, login_url=None):
	"""
	Decorator for views that checks whether a user has a particular permission
	enabled, redirecting to the log-in page or rendering a 403 as necessary.
	"""
	return user_passes_test_or_403(lambda u: u.has_perm(perm),
		login_url=login_url)


def view_or_basicauth(view, request, test_func, realm="", *args, **kwargs):
	"""
	http://djangosnippets.org/snippets/243/

	This is a helper function used by both 'logged_in_or_basicauth' and
	'has_perm_or_basicauth' that does the nitty of determining if they
	are already logged in or if they have provided proper http-authorization
	and returning the view if all goes well, otherwise responding with a 401.
	"""
	if test_func(request.user):
		# Already logged in, just return the view.
		return view(request, *args, **kwargs)

	# They are not logged in. See if they provided login credentials
	if 'HTTP_AUTHORIZATION' in request.META:
		auth = request.META['HTTP_AUTHORIZATION'].split()
		if len(auth) == 2:
			# NOTE: We are only support basic authentication for now.
			if auth[0].lower() == "basic":
				uname, passwd = base64.b64decode(auth[1]).split(':')
				user = authenticate(username=uname, password=passwd)
				if user is not None:
					if user.is_active:
						login(request, user)
						request.user = user
						return view(request, *args, **kwargs)

	# Either they did not provide an authorization header or
	# something in the authorization attempt failed. Send a 401
	# back to them to ask them to authenticate.
	#
	response = HttpResponse()
	response.status_code = 401
	response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
	return response


def logged_in_or_basicauth(realm=""):
	"""
	http://djangosnippets.org/snippets/243/

	A simple decorator that requires a user to be logged in. If they are not
	logged in the request is examined for a 'authorization' header.

	If the header is present it is tested for basic authentication and
	the user is logged in with the provided credentials.

	If the header is not present a http 401 is sent back to the
	requestor to provide credentials.

	The purpose of this is that in several django projects I have needed
	several specific views that need to support basic authentication, yet the
	web site as a whole used django's provided authentication.

	The uses for this are for urls that are access programmatically such as
	by rss feed readers, yet the view requires a user to be logged in. Many rss
	readers support supplying the authentication credentials via http basic
	auth (and they do NOT support a redirect to a form where they post a
	username/password.)

	Use is simple:

	@logged_in_or_basicauth()
	def your_view:
		...

	You can provide the name of the realm to ask for authentication within.
	"""
	def view_decorator(func):
		def wrapper(request, *args, **kwargs):
			return view_or_basicauth(func, request,
				lambda u: u.is_authenticated(),
				realm, *args, **kwargs)
		return wrapper
	return view_decorator


def user_passes_test_or_basicauth(test_func, realm = ""):
	"""
	Based on http://djangosnippets.org/snippets/243/
	"""
	def view_decorator(func):
		def wrapper(request, *args, **kwargs):
			return view_or_basicauth(func, request,
				test_func,
				realm, *args, **kwargs)
		return wrapper
	return view_decorator
