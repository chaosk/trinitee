from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def has_unreads(topic, user):
    """
    Check if topic has messages which user didn't read.
    """
    if not user.is_authenticated() or\
        (user.posttracking.last_read is not None and\
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
    if not user.is_authenticated() or\
        (user.posttracking.last_read is not None and\
         user.posttracking.last_read > post.created_at):
            return False
    else:
        if isinstance(user.posttracking.topics, dict):
            if post.id > user.posttracking.topics.get(str(post.topic.id), 0):
                return True
            else:
                return False
        return True

@register.filter
def editable_by(post, user):
	"""
	Check if the post could be edited by the user.
	"""
	if user.has_perm('forums.edit_post') or post.user == user:
		return True
	return False

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
			html = u' '.join([page_link % (1 ,1), u'&hellip;'] + \
				[page_link % (page, page) \
				for page in xrange(pages - 2, pages + 1)])
	return mark_safe(html)