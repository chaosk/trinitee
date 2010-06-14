import datetime
import pytz
from django.utils import dateformat
from accounts.models import UserProfile
from utils.annoying.functions import get_config, get_object_or_None


def user_timezone(dt, user):
	"""
	Converts the given datetime to the given User's timezone, if they
	have one set in their forum profile.

	Adapted from http://www.djangosnippets.org/snippets/183/
	"""
	tz = get_config('TIME_ZONE', 'UTC')
	if user.is_authenticated():
		if user.profile.timezone:
			tz = user.profile.timezone
	try:
		result = dt.astimezone(pytz.timezone(tz))
	except ValueError:
		# The datetime was stored without timezone info, so use the
		# timezone configured in settings.
		result = dt.replace(tzinfo=pytz.timezone(get_config('TIME_ZONE', 'UTC'))) \
			.astimezone(pytz.timezone(tz))
	return result


def format_datetime(dt, user, date_format, time_format, separator=' '):
	"""
	Formats a datetime, using ``'Today'`` or ``'Yesterday'`` instead of
	the given date format when appropriate.

	If a User is given and they have a timezone set in their profile,
	the datetime will be translated to their local time.
	"""
	if user:
		dt = user_timezone(dt, user)
		today = user_timezone(datetime.datetime.now(), user).date()
	else:
		today = datetime.date.today()
	date_part = dt.date()
	delta = date_part - today
	if delta.days == 0:
		date = u'Today'
	elif delta.days == -1:
		date = u'Yesterday'
	else:
		date = dateformat.format(dt, date_format)
	return u'%s%s%s' % (date, separator,
		dateformat.time_format(dt.time(), time_format))
