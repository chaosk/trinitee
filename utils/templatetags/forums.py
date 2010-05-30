from django import template

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