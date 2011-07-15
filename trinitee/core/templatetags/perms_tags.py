from django import template
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group, User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from core.perms.utilities import get_codename_perms
from guardian.exceptions import NotUserNorGroup

register = template.Library()


class PermissionsNode(template.Node):
	def __init__(self, for_whom, model, context_var):
		self.for_whom = template.Variable(for_whom)
		self.model = template.Variable(model)
		self.context_var = context_var

	def render(self, context):
		for_whom = self.for_whom.resolve(context)
		if isinstance(for_whom, User):
			self.user = for_whom
			self.group = None
		elif isinstance(for_whom, AnonymousUser):
			self.user = User.get_anonymous()
			self.group = None
		elif isinstance(for_whom, Group):
			self.user = None
			self.group = for_whom
		else:
			raise NotUserNorGroup("User or Group instance required (got %s)"
				% for_whom.__class__)
		model = self.model.resolve(context)
		perms = get_codename_perms(model)
		context[self.context_var] = perms
		return ''


@register.tag
def get_model_perms(parser, token):
	"""
	Returns a list of permissions (as ``codename`` strings) for a given
	``user``/``group`` and ``model`` (Model class).

	Parses ``get_model_perms`` tag which should be in format::

		{% get_model_perms user/group for model as "context_var" %}

	Example of usage (assuming ``model`` and ``perm`` objects are
	available from *context*)::

		{% get_obj_perms request.user for model as "flatpage_perms" %}

		{% if "delete_flatpage" in flatpage_perms %}
			<a href="/pages/delete?target={{ flatpage.url }}">Remove page</a>
		{% endif %}

	"""
	bits = token.split_contents()
	format = '{% get_obj_perms user/group for model as "context_var" %}'
	if len(bits) != 6 or bits[2] != 'for' or bits[4] != 'as':
		raise template.TemplateSyntaxError("get_model_perms tag should be in "
			"format: %s" % format)

	for_whom = bits[1]
	obj = bits[3]
	context_var = bits[5]
	if context_var[0] != context_var[-1] or context_var[0] not in ('"', "'"):
		raise template.TemplateSyntaxError("get_model_perms tag's context_var "
			"argument should be in quotes")
	context_var = context_var[1:-1]
	return PermissionsNode(for_whom, obj, context_var)

class PermsEditNode(template.Node):
	def __init__(self, for_whom, obj):
		self.actor = template.Variable(for_whom)
		self.obj = template.Variable(obj)

	def render(self, context):
		actor = self.actor.resolve(context)
		target = context['model']
		if isinstance(actor, User):
			actor_type = 'user'
		elif isinstance(actor, Group):
			actor_type = 'group'
		else:
			raise AttributeError("unrecognized actor, has to be User or Group object")
		target_ct_id = ContentType.objects.get_for_model(target).id
		extra_context = {
			'target_ct_id': target_ct_id,
			'actor_type': actor_type,
			'actor_obj_id': actor.id,
		}
		try:
			extra_context['target_obj_id'] = target.id
		except AttributeError:
			pass
		return reverse('core.perms.views.perms_edit', kwargs=extra_context)


@register.tag
def perms_edit_url(parser, token):
	bits = token.split_contents()
	format = '{% perms_edit_url user/group obj/model %}'
	if len(bits) !=3:
		raise template.TemplateSyntaxError("perms_edit_url tag should be in "
			"format: %s" % format)
	for_whom = bits[1]
	obj = bits[2]
	return PermsEditNode(for_whom, obj)