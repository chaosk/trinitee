from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('wiki.views',
	url(r'^new/$', 'wiki_new', name='wiki_new'),
	url(r'^history/(?P<slug>[\w\W]+)$', 'wiki_history', name='wiki_history'),
	url(r'^edit/(?P<slug>[\w\W]+)$', 'wiki_edit', name='wiki_edit'),
	url(r'^(?P<slug>[\w\W]+)$', 'wiki_detail', name='wiki_detail'),
	url(r'^$', 'wiki_index', name='wiki_index'),
)
