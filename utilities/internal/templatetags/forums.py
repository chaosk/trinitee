from urllib import quote
from django import template
from django.core.cache import cache
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def has_unreads(topic, user):
	"""
	Check if topic has messages which user didn't read.
	"""
	if not user.is_authenticated() or \
		(user.posttracking.last_read is not None and \
		user.posttracking.last_read > topic.last_post.created_at):
		return False
	else:
		if isinstance(user.posttracking.topics, dict):
			if topic.last_post.id > user.posttracking.topics.get(str(topic.id), 0):
				return True
			else:
				return False
		return True


@register.filter
def is_unread(post, user):
	"""
	Check if post wasn't read by user.
	"""
	if not user.is_authenticated() or \
		(user.posttracking.last_read is not None and \
		user.posttracking.last_read > topic.last_post.created_at):
		return False
	else:
		if isinstance(user.posttracking.topics, dict):
			if post.id > user.posttracking.topics.get(str(post.topic.id), 0):
				return True
			else:
				return False
		return True


@register.filter
def topic_pagination(topic, posts_per_page):
	"""
	Creates topic listing page links for the given topic, with the given
	number of posts per page.

	Topics with between 2 and 5 pages will have page links displayed for
	each page.

	Topics with more than 5 pages will have page links displayed for the
	first page and the last 3 pages.
	"""
	hits = (topic.post_count - 1)
	if hits < 1:
		hits = 0
	pages = hits // posts_per_page + 1
	if pages < 2:
		html = u''
	else:
		page_link = u'<a class="pagelink" href="%s?page=%%s">%%s</a>' % \
			topic.get_absolute_url()
		if pages < 6:
			html = u' '.join([page_link % (page, page) \
				for page in xrange(1, pages + 1)])
		else:
			html = u' '.join([page_link % (1, 1), u'&hellip;'] + \
				[page_link % (page, page) \
				for page in xrange(pages - 2, pages + 1)])
	return mark_safe(html)


@register.filter
def can_access_forum(request, forum, return_plain_boolean=False, login_url=None):
	if request.user.is_staff or request.user.is_superuser:
		return True
	if not login_url:
		from django.conf import settings
		login_url = settings.LOGIN_URL
	forum_can_read_groups = cache.get('forums_forum_can_read_%s' % forum)
	if forum_can_read_groups is None:
		forum_can_read_groups = forum.can_read.values_list('id', flat=True)
		cache.set('forums_forum_can_read_%s' % forum,
			forum_can_read_groups, 86400)
	group = request.user.profile.group if request.user.is_authenticated() else 1
	if hasattr(forum, 'num_can_read'):
		num_can_read = forum.num_can_read
	else:
		num_can_read = len(forum_can_read_groups)

	if num_can_read and not group in forum_can_read_groups:
		if not request.user.is_authenticated():
			return False if return_plain_boolean else \
				HttpResponseRedirect('%s?%s=%s' % (login_url,
				REDIRECT_FIELD_NAME, quote(request.get_full_path())))
		resp = render_to_response('403.html',
			context_instance=RequestContext(request))
		resp.status_code = 403
		return False if return_plain_boolean else resp
	return True


@register.filter
def can_post_topic(user, forum):
	can_post_topic_groups = forum.can_post_topic.all()
	if len(can_post_topic_groups)and \
		not user.profile.group in forum.can_post_topic.all() and \
		not user.is_superuser:
		return False
	return True


@register.filter
def can_post_reply(user, forum):
	can_post_reply_groups = forum.can_post_reply.all()
	if len(can_post_reply_groups) and \
		not user.profile.group in can_post_reply_groups and \
		not user.is_superuser:
		return False
	return True


@register.filter
def current_karma(post, user):
	if not hasattr(user, 'karma'):
		return 0
	try:
		return user.karma.filter(post=post)[0].karma
	except IndexError:
		return 0
