from django.shortcuts import get_object_or_404
from annoying.decorators import render_to
from wiki.models import WikiPage


@render_to('wiki/index.html')
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


def wiki_new(request):
	raise NotImplementedError


def wiki_edit(request, slug):
	raise NotImplementedError


def wiki_history(request, slug):
	raise NotImplementedError


def wiki_history_detail(request, slug, rev):
	raise NotImplementedError


def wiki_compare(request, slug, rev_from, rev_to):
	raise NotImplementedError
