from django import template
from django.utils.safestring import mark_safe
from trinitee.utils.dates import format_datetime

register = template.Library()

@register.filter
def user_date(st, user=None):
	"""
	Formats a general datetime.
	"""
	return mark_safe(format_datetime(st, user, 'Y-m-d', 'H:i:s', ' '))