from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('wiki.views',
	url(r'^new/$', 'wiki_new', name='wiki_new'),
	url(r'^list/$', 'wiki_list', name='wiki_list'),
	url(r'^(?P<slug>[^/]+)/(?P<rev>\d+)/$',
		'wiki_history_detail', name='wiki_history_detail'),
	url(r'^(?P<slug>[^/]+)/compare/(?P<rev_from>\d+)\.\.\.(?P<rev_to>\d+)/$',
	 	'wiki_compare', name='wiki_compare'),
	url(r'^(?P<slug>[^/]+)/history/$', 'wiki_history', name='wiki_history'),
	url(r'^(?P<slug>[^/]+)/revert/(?P<rev>\d+)/$', 'wiki_revert',
		name='wiki_revert'),
	url(r'^(?P<slug>[^/]+)/restore/(?P<rev>\d+)/$',
		'wiki_restore', name='wiki_restore'),
	url(r'^(?P<slug>[^/]+)/edit/$', 'wiki_edit', name='wiki_edit'),
	url(r'^(?P<slug>[^/]+)/delete/$', 'wiki_delete', name='wiki_delete'),
	url(r'^(?P<slug>[^/]+)$', 'wiki_detail', name='wiki_detail'),
	url(r'^$', 'wiki_index', name='wiki_index'),
)
