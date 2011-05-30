from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from annoying.decorators import render_to
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
	page = get_object_or_404(WikiPage, slug=slug)
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


def wiki_history(request, slug):
	raise NotImplementedError


def wiki_history_detail(request, slug, rev):
	raise NotImplementedError


def wiki_compare(request, slug, rev_from, rev_to):
	raise NotImplementedError
