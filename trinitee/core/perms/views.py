from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from annoying.decorators import render_to
from guardian.forms import (GroupObjectPermissionsForm,
	UserObjectPermissionsForm)
from guardian.shortcuts import get_users_with_perms
from guardian.utils import get_anonymous_user


@render_to('core/perms/detail.html')
@login_required
def perms_detail(request, contenttype_id, object_id):
	if not request.user.is_staff:
		raise Http404

	content_type = get_object_or_404(ContentType, pk=contenttype_id)
	model = content_type.model_class()
	try:
		obj = content_type.get_object_for_this_type(pk=object_id)
	except model.DoesNotExist():
		raise Http404

	actors = list(Group.objects.all())
	anonymous = get_anonymous_user()
	# adding anonymous user
	actors.append(anonymous)
	# adding users with custom permissions
	# (excluding anonymous user from this qs)
	actors += list(get_users_with_perms(obj,
		with_group_users=False).exclude(pk=anonymous.id))

	return {
		'perms_to_check': model._meta.permissions,
		'actors': actors,
		'object': obj,
		'obj_ct_id': contenttype_id,
	}


@render_to('core/perms/edit.html')
@login_required
def perms_edit(request, target_ct_id, target_obj_id, actor_type, actor_obj_id):
	if not request.user.is_staff or not actor_type in ('user', 'group'):
		raise Http404

	target_ct = get_object_or_404(ContentType, pk=target_ct_id)
	target_model = target_ct.model_class()
	try:
		target = target_ct.get_object_for_this_type(pk=target_obj_id)
	except target_model.DoesNotExist():
		raise Http404

	if actor_type == 'group':
		form = GroupObjectPermissionsForm
		actor_model = Group
	else:
		form = UserObjectPermissionsForm
		actor_model = User

	try:
		actor = actor_model.objects.get(pk=actor_obj_id)
	except actor_model.DoesNotExist():
		raise Http404

	perms_to_check = target_model._meta.permissions

	form = form(actor, target, request.POST or None)
	if request.method == 'POST' and form.is_valid():
		form.save_obj_perms()
		messages.success(request, "Successfully changed permissions")
		return redirect(target.get_permissions_url())

	return {
		'form': form,
		'perms_to_check': perms_to_check,
		'actor': actor,
		'target': target,
	}


# TODO DRY
#      ajaxify
#      add to urlpatterns
@login_required
def perms_edit_inline(request):
	if request.method != 'POST':
		return False
	
	data = request.POST.cleaned_data
	actor_type = data.get('actor_type')
	if not request.user.is_staff or not actor_type in ('user', 'group'):
		return False

	target_ct = get_object_or_404(ContentType, pk=data.get('target_ct_id'))
	target_model = target_ct.model_class()
	try:
		target = target_ct.get_object_for_this_type(pk=data.get('target_obj_id'))
	except target_model.DoesNotExist():
		raise Http404

	if actor_type == 'group':
		form = GroupObjectPermissionsForm
		actor_model = Group
	else:
		form = UserObjectPermissionsForm
		actor_model = User

	try:
		actor = actor_model.objects.get(pk=data.get('actor_obj_id'))
	except actor_model.DoesNotExist():
		raise Http404

	perms_to_check = target_model._meta.permissions

	for perm, value in data.get('perms'):
		if value:
			assign(perm, actor, target)
		else:
			remove_perm(perm, actor, target)

	return True