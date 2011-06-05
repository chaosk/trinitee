from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('wiki.views',
	url(r'^_new/?$', 'wiki_new', name='wiki_new'),
	url(r'^_list/?$', 'wiki_list', name='wiki_list'),
	url(r'^(?P<slug>[^/]+)/_history/(?P<rev_from>\d+)\.\.\.(?P<rev_to>\d+)/$',
	 	'wiki_compare', name='wiki_compare'),
	url(r'^(?P<slug>[^/]+)/_history/(?P<rev>\d+)/$',
		'wiki_history_detail', name='wiki_history_detail'),
	url(r'^(?P<slug>[^/]+)/_history/$', 'wiki_history', name='wiki_history'),
	url(r'^(?P<slug>[^/]+)/_edit/$', 'wiki_edit', name='wiki_edit'),
	url(r'^(?P<slug>[^/]+)/_delete/$', 'wiki_delete', name='wiki_delete'),
	url(r'^(?P<slug>[^/]+)$', 'wiki_detail', name='wiki_detail'),
	url(r'^$', 'wiki_index', name='wiki_index'),
)
