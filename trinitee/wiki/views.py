from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404
from annoying.decorators import render_to
from reversion import revision
from reversion.helpers import generate_patch_html
from reversion.models import Version
from wiki.forms import WikiNewForm, WikiEditForm
from wiki.models import WikiPage


@render_to('wiki/detail.html')
def wiki_index(request):
	""" Returns Index wiki page """
	page, created = WikiPage.objects.get_or_create(slug='Index',
		defaults={'title': u'Index'}
	)
	return {
		'page': page,
	}


@render_to('wiki/detail.html')
def wiki_detail(request, slug):
	try:
		page = WikiPage.objects.get(slug=slug)
	except WikiPage.DoesNotExist:
		deleted_versions = Version.objects.get_deleted(WikiPage)[:5]
		deleted_version = None
		for version in deleted_versions:
			if version.get_field_dict().get('slug') == slug:
				deleted_version = version
				break
		if not deleted_version:
			raise Http404
		else:
			return redirect(reverse('wiki_restore', kwargs={
				'slug': slug,
				'rev': deleted_version.id,
			}))
	return {
		'page': page,
	}


@render_to('wiki/new.html')
def wiki_new(request):
	form = WikiNewForm()
	if request.method == 'POST':
		form = WikiNewForm(request.POST)
		if form.is_valid():
			new_page = form.save()
			messages.success(request, "New page has been added to the wiki.")
			revision.comment = "Initial version"
			return redirect(new_page.get_absolute_url())
	return {
		'form': form,
	}


@render_to('wiki/edit.html')
def wiki_edit(request, slug):
	page = get_object_or_404(WikiPage, slug=slug)
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
	return {
		'page': page,
		'form': form,
	}


@render_to('wiki/delete.html')
def wiki_delete(request, slug):
	page = get_object_or_404(WikiPage, slug=slug)
	if request.method == 'POST':
		page.delete()
		messages.success(request,
			"Successfully removed \"{0}\" page.".format(page)
		)
		return redirect(reverse('wiki_index'))
	return {
		'page': page,
	}


@render_to('wiki/list.html')
def wiki_list(request):
	return {
		'pages': WikiPage.objects.all()
	}


@render_to('wiki/history.html')
def wiki_history(request, slug):
	page = get_object_or_404(WikiPage, slug=slug)
	versions = Version.objects.get_for_object(page).select_related() \
		.order_by('-id')
	latest_version_id = versions[0].id
	return {
		'page': page,
		'latest_version_id': latest_version_id,
		'versions': versions,
	}


@render_to('wiki/history_detail.html')
def wiki_history_detail(request, slug, rev):
	page = get_object_or_404(WikiPage, slug=slug)
	try:
		version = Version.objects.get(pk=rev)
	except Version.DoesNotExist:
		raise Http404
	if page.id != version.object_id:
		raise Http404
	return {
		'page': version.get_field_dict(),
		'revision': version.revision,
	}


@render_to('wiki/compare.html')
def wiki_compare(request, slug, rev_from, rev_to):
	page = get_object_or_404(WikiPage, slug=slug)
	try:
		version_from = Version.objects.get(pk=rev_from)
		version_to = Version.objects.get(pk=rev_to)
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
	return {
		'page': page,
		'patch_html': patch_html,
		'revision_from': revision_from,
		'revision_to': revision_to,
	}


@render_to("wiki/revert.html")
def wiki_revert(request, slug, rev):
	page = get_object_or_404(WikiPage, slug=slug)
	version = get_object_or_404(Version, pk=rev)
	if page.id != int(version.object_id):
		messages.error(request,
			"You have tried to revert this page to another page object."
		)
		return redirect(reverse('wiki_history', kwargs={'slug': slug}))
	if request.method == 'POST':
		version.revert()
		messages.success(request,
			"Successfully reverted \"{0}\" page to state from {1}.".format(
				page, version.revision.date_created
			)
		)
		return redirect(reverse('wiki_detail', kwargs={'slug': slug}))
	return {
		'page': page,
		'version': version,
	}


@render_to("wiki/restore.html")
def wiki_restore(request, slug, rev):
	version = get_object_or_404(Version, pk=rev)
	if request.method == 'POST':
		version.revert()
		messages.success(request,
			"Successfully restored \"{0}\" page to state from {1}.".format(
				version.get_field_dict().get('title'),
				version.revision.date_created
			)
		)
		return redirect(reverse('wiki_detail', kwargs={'slug': slug}))
	return {
		'version': version,
	}
