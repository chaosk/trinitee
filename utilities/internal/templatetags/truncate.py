from django import template

register = template.Library()


@register.filter
def truncate(value, limit=80):
	"""
	http://djangosnippets.org/snippets/1259/
	
	Truncates a string after a given number of chars keeping whole words.

	Usage:
	{{ string|truncate }}
	{{ string|truncate:50 }}
	"""

	try:
		limit = int(limit)
	except ValueError:
		return value
	value = unicode(value)
	if len(value) <= limit:
		return value
	value = value[:limit]
	words = value.split(' ')[:-1]
	return ' '.join(words) + '...'
