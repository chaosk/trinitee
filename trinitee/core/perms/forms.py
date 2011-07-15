from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from core.perms.utilities import get_codename_perms
from guardian.shortcuts import assign
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_perms_for_model


class BasePermissionsForm(forms.Form):
	"""
	Base form for global permissions management. Needs to be extended for usage
	with users and/or groups.
	"""

	def __init__(self, model, *args, **kwargs):
		"""
		:param obj: Any instance which form would use to manage permissions
		"""
		self.model = model
		super(BasePermissionsForm, self).__init__(*args, **kwargs)
		field_name = self.get_perms_field_name()
		self.fields[field_name] = self.get_perms_field()

	def get_perms_field(self):
		"""
		Returns field instance for permissions management. May be
		replaced entirely.
		"""
		field_class = self.get_perms_field_class()
		field = field_class(
			label=self.get_perms_field_label(),
			choices=self.get_perms_field_choices(),
			initial=self.get_perms_field_initial(),
			widget=self.get_perms_field_widget(),
			required=self.are_perms_required(),
		)
		return field

	def get_perms_field_name(self):
		"""
		Returns name of the permissions management field. Default:
		``permission``.
		"""
		return 'permissions'

	def get_perms_field_label(self):
		"""
		Returns label of the permissions management field. Default:
		``_("Permissions")`` (marked to be translated).
		"""
		return _("Permissions")

	def get_perms_field_choices(self):
		"""
		Returns choices for permissions management field. Default:
		list of tuples ``(codename, name)`` for each ``Permission`` instance
		for the managed model.
		"""
		choices = [(p.codename, p.name) for p in get_perms_for_model(self.model)]
		return choices

	def get_perms_field_initial(self):
		"""
		Returns initial permissions management field choices. Default:
		``[]`` (empty list).
		"""
		return []

	def get_perms_field_class(self):
		"""
		Returns permissions management field's base class. Default:
		``django.forms.MultipleChoiceField``.
		"""
		return forms.MultipleChoiceField

	def get_perms_field_widget(self):
		"""
		Returns permissions management field's widget base class.
		Default: ``django.forms.SelectMultiple``.
		"""
		return forms.SelectMultiple

	def are_perms_required(self):
		"""
		Indicates if at least one permission should be required. Default:
		``False``.
		"""
		return False

	def save_perms(self):
		"""
		Must be implemented in concrete form class. This method should store
		selected permissions.
		"""
		raise NotImplementedError


class UserPermissionsForm(BasePermissionsForm):
	"""
	Global permissions management form for usage with ``User`` instances.

	Example usage::

		from django.contrib.auth.models import User
		from django.shortcuts import get_object_or_404
		from myapp.models import Post
		from core.perms.forms import UserPermissionsForm

		def my_view(request, user_id):
			user = get_object_or_404(User, id=user_id)
			form = UserPermissionsForm(user, Post, request.POST or None)
			if request.method == 'POST' and form.is_valid():
				form.save_perms()
			...

	"""

	def __init__(self, user, *args, **kwargs):
		self.user = user
		super(UserPermissionsForm, self).__init__(*args, **kwargs)

	def get_perms_field_initial(self):
		user_perms = set(self.user.get_all_permissions())
		model_perms = set(get_codename_perms(self.model))
		perms = user_perms.intersection(model_perms)
		return perms

	def save_perms(self):
		"""
		Saves selected permissions by creating new ones and removing
		those which were not selected but already exists.

		Should be called *after* form is validated.
		"""
		perms = self.cleaned_data[self.get_perms_field_name()]
		model_perms = [c[0] for c in self.get_perms_field_choices()]

		# woo.
		app_label = ContentType.objects.get_for_model(self.model).app_label

		to_remove = set(model_perms) - set(perms)
		for perm in to_remove:
			remove_perm("{0}.{1}".format(app_label, perm), self.user)

		for perm in perms:
			assign("{0}.{1}".format(app_label, perm), self.user)


class GroupPermissionsForm(BasePermissionsForm):
	"""
	Global permissions management form for usage with ``Group`` instances.

	Example usage::

		from django.contrib.auth.models import Group
		from django.shortcuts import get_object_or_404
		from myapp.models import Post
		from core.perms.forms import GroupPermissionsForm

		def my_view(request, group_id):
			group = get_object_or_404(Group, id=group_id)
			form = GroupPermissionsForm(group, Post, request.POST or None)
			if request.method == 'POST' and form.is_valid():
				form.save_perms()
			...

	"""

	def __init__(self, group, *args, **kwargs):
		self.group = group
		super(GroupPermissionsForm, self).__init__(*args, **kwargs)

	def get_perms_field_initial(self):
		group_perms = set(self.group.permissions.all())
		model_perms = set(get_codename_perms(self.model))
		perms = group_perms.intersection(model_perms)
		return perms

	def save_perms(self):
		"""
		Saves selected permissions by creating new ones and removing
		those which were not selected but already exists.

		Should be called *after* form is validated.
		"""
		perms = self.cleaned_data[self.get_perms_field_name()]
		model_perms = [c[0] for c in self.get_perms_field_choices()]

		# woo.
		app_label = ContentType.objects.get_for_model(self.model).app_label

		to_remove = set(model_perms) - set(perms)
		for perm in to_remove:
			remove_perm("{0}.{1}".format(app_label, perm), self.group)

		for perm in perms:
			assign("{0}.{1}".format(app_label, perm), self.group)
