from django.shortcuts import get_object_or_404
from annoying.decorators import render_to
from wiki.models import WikiPage


@render_to('wiki/index.html')
def wiki_index(request):
	""" Returns Index wiki page """
	page, created = WikiPage.objects.get_or_create(slug='Index',
		defaults={'title': 'Index'}
	)
	return {
		'page': page,
	}
