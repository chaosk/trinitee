from django import template
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.simple_tag
def perms_edit_url(target, actor):
	if isinstance(actor, User):
		actor_type = 'user'
	elif isinstance(actor, Group):
		actor_type = 'group'
	else:
		raise AttributeError("unrecognized actor, have to be User or Group object")
	target_ct_id = ContentType.objects.get_for_model(target.__class__).id
	actor
	return reverse('core.perms.views.perms_edit', kwargs={
		'target_ct_id': target_ct_id,
		'target_obj_id': target.id,
		'actor_type': actor_type,
		'actor_obj_id': actor.id,
	})