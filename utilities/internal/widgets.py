from django import forms
from django.utils.safestring import mark_safe
from forums.models import Post
from utilities.annoying.functions import get_config
from utilities.internal.templatetags.truncate import truncate

class PostPreviewWidget(forms.Widget):
	def render(self, name, value, attrs=None):
		if value is None:
			return ''
		if not name == 'post':
			raise ValueError('PostPreviewWidget can be used with Post model only.')
		post = Post.objects.get(pk=value)
		return '<input type="hidden" name="%s" value="%s"><a href="%s">%s</a><br /><i>%s</i>' % \
			(name, value, post.get_absolute_url(), post, truncate(post.content, 80))

class NullBooleanROWidget(forms.Widget):
	def render(self, name, value, attrs=None):
		if value is None:
			icon = 'unknown'
		elif value:
			icon = 'yes'
		elif not value:
			icon = 'no'
		else:
			raise ValueError('NullBooleanROWidget can be used with boolean and None values only.')
		return mark_safe(u'<img src="%simg/admin/icon-%s.gif" />' % \
			(get_config('ADMIN_MEDIA_PREFIX', '/static/admin/'), icon))
