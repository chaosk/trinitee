from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('forums.views',
	url(r'^$', 'forums_index', name='forums_index'),
	url(r'^(?P<category_id>\d+)/$', 'topic_list', name='topic_list'),
	url(r'^(?P<category_id>\d+)/new/$', 'topic_new', name='topic_new'),
	url(r'^(?P<category_id>\d+)/(?P<topic_id>\d+)/$', 'topic_detail',
		name='topic_detail'),
	url(r'^(?P<category_id>\d+)/(?P<topic_id>\d+)/qmod/$',
		'topic_quick_moderation', name='topic_quick_moderation'),
	url(r'^(?P<category_id>\d+)/(?P<topic_id>\d+)/reply/$', 'post_new',
		name='post_new'),
	url(r'^post/(?P<post_id>\d+)/$', 'post_permalink',
		name='post_permalink'),
)
