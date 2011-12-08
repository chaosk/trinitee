from datetime import datetime
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.template.response import TemplateResponse
from reversion import revision
from reversion.helpers import generate_patch_html
from reversion.models import Version
from wiki.forms import WikiNewForm, WikiEditForm
from wiki.models import WikiPage


def wiki_index(request):
	""" Returns Index wiki page """
	page, created = WikiPage.objects.get_or_create(slug='Index',
		defaults={'title': u'Index'}
	)
	return TemplateResponse(request, 'wiki/detail.html', {
		'page': page,
	})


def wiki_detail(request, slug):
	try:
		page = WikiPage.objects.get(slug=slug)
	except WikiPage.DoesNotExist:
		deleted_versions = Version.objects.get_deleted(WikiPage)[:5]
		deleted_version = None
		for version in deleted_versions:
			if version.field_dict.get('slug') == slug:
				deleted_version = version
				break
		if not deleted_version:
			raise Http404
		else:
			return redirect(reverse('wiki_restore', kwargs={
				'slug': slug,
				'rev': deleted_version.id,
			}))
	return TemplateResponse(request, 'wiki/detail.html', {
		'page': page,
	})


def wiki_new(request):
	if not request.user.has_perm('wiki.add_wikipage'):
		return HttpResponseForbidden()
	form = WikiNewForm()
	if request.method == 'POST':
		form = WikiNewForm(request.POST)
		if form.is_valid():
			new_page = form.save()
			messages.success(request, "New page has been added to the wiki.")
			revision.comment = "Initial version"
			return redirect(new_page.get_absolute_url())
	return TemplateResponse(request, 'wiki/new.html', {
		'form': form,
	})


def wiki_edit(request, slug):
	page = get_object_or_404(WikiPage, slug=slug)
	if not request.user.has_perm('wiki.edit_wikipage'):
		return HttpResponseForbidden()
	form = WikiEditForm(instance=page)
	if request.method == 'POST':
		form = WikiEditForm(request.POST, instance=page)
		if form.is_valid():
			form.save()
			messages.success(request,
				"Successfully updated \"{0}\" page.".format(page)
			)
			revision.comment = form.cleaned_data.get('comment')
			return redirect(page.get_absolute_url())
	return TemplateResponse(request, 'wiki/edit.html', {
		'page': page,
		'form': form,
	})


def wiki_delete(request, slug):
	page = get_object_or_404(WikiPage, slug=slug)
	if not request.user.has_perm('wiki.delete_wikipage'):
		return HttpResponseForbidden()
	if request.method == 'POST':
		page.delete()
		messages.success(request,
			"Successfully removed \"{0}\" page.".format(page)
		)
		revision.comment = "Page deleted"
		return redirect(reverse('wiki_index'))
	return TemplateResponse(request, 'wiki/delete.html', {
		'page': page,
	})


def wiki_list(request):
	return TemplateResponse(request, 'wiki/list.html', {
		'pages': WikiPage.objects.all(),
		'permissions_url': WikiPage().get_permissions_url(), # hackish
	})


def wiki_history(request, slug):
	page = get_object_or_404(WikiPage, slug=slug)
	versions = Version.objects.get_for_object(page).select_related() \
		.order_by('-id')
	try:
		latest_version_id = versions[0].id
	except IndexError:
		latest_version_id = None
	return TemplateResponse(request, 'wiki/history.html', {
		'page': page,
		'latest_version_id': latest_version_id,
		'versions': versions,
	})


def wiki_history_detail(request, slug, rev):
	page = get_object_or_404(WikiPage, slug=slug)
	try:
		version = Version.objects.select_related().get(pk=rev)
	except Version.DoesNotExist:
		raise Http404
	if page.id != int(version.object_id):
		raise Http404
	return TemplateResponse(request, 'wiki/history_detail.html', {
		'page': version.field_dict,
		'revision': version.revision,
	})


def wiki_compare(request, slug, rev_from, rev_to):
	page = get_object_or_404(WikiPage, slug=slug)
	try:
		version_from = Version.objects.select_related().get(pk=rev_from)
		version_to = Version.objects.select_related().get(pk=rev_to)
	except Version.DoesNotExist:
		raise Http404
	if page.id != int(version_from.object_id) or \
		int(version_from.object_id) != int(version_to.object_id):
		messages.error(request,
			"You have tried to compare revisions of different pages."
		)
		return redirect(reverse('wiki_history', kwargs={'slug': slug}))
	revision_to = version_to.revision
	revision_from = version_from.revision
	patch_html = generate_patch_html(version_from, version_to, "content")
	return TemplateResponse(request, 'wiki/compare.html', {
		'page': page,
		'patch_html': patch_html,
		'revision_from': revision_from,
		'revision_to': revision_to,
	})


def wiki_revert(request, slug, rev):
	if not request.user.has_perm('wiki.moderate_wikipage'):
		return HttpResponseForbidden()
	page = get_object_or_404(WikiPage, slug=slug)
	version = get_object_or_404(Version.objects.select_related(), pk=rev)
	if page.id != int(version.object_id):
		messages.error(request,
			"You have tried to revert this page to another page object."
		)
		return redirect(reverse('wiki_history', kwargs={'slug': slug}))
	if request.method == 'POST':
		version.revert()
		messages.success(request,
			"Successfully reverted \"{0}\" page to state from {1}.".format(
				page,
				datetime.strftime(version.revision.date_created,
					"%B %d, %Y, %I:%M %p"
				)
			)
		)
		revision.comment = "Reverted to #{0}".format(version.id)
		return redirect(reverse('wiki_detail', kwargs={'slug': slug}))
	return TemplateResponse(request, 'wiki/revert.html', {
		'page': page,
		'version': version,
	})


def wiki_restore(request, slug, rev):
	if not request.user.has_perm('wiki.moderate_wikipage'):
		return HttpResponseForbidden()
	version = get_object_or_404(Version, pk=rev)
	if request.method == 'POST':
		version.revert()
		messages.success(request,
			"Successfully restored \"{0}\" page to state from {1}.".format(
				version.field_dict.get('title'),
				datetime.strftime(version.revision.date_created, 
					"%B %d, %Y, %I:%M %p"
				)
			)
		)
		revision.comment = "Page restored"
		return redirect(reverse('wiki_detail', kwargs={'slug': slug}))
	return TemplateResponse(request, 'wiki/restore.html', {
		'version': version,
	})
