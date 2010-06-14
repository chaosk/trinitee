import re
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


@register.tag
def smartspaceless(parser, token):
	nodelist = parser.parse(('endsmartspaceless',))
	parser.delete_first_token()
	return SmartSpacelessNode(nodelist)


class SmartSpacelessNode(template.Node):
	"""
	http://djangosnippets.org/snippets/620/
	"""
	def __init__(self, nodelist):
		self.nodelist = nodelist

	def render(self, context):
		s = self.nodelist.render(context).strip()
		inline_tags = 'a|b|i|u|em|strong|sup|sub|tt|font|small|big'
		inlines_with_spaces = r'</(%s)>\s+<(%s)\b' % (inline_tags, inline_tags)
		s = re.sub(inlines_with_spaces, r'</\1>&#preservespace;<\2', s)
		s = re.sub(r'>\s+<', '><', s)
		s = s.replace('&#preservespace;', ' ')
		return s
