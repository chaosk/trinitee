from django.conf.urls.defaults import *

urlpatterns = patterns('trinitee.forums.views',
	(r'^$', 'index'),
	url(r'^forum/(?P<forum_id>\d+)/$', 'forum_view', name='forum_view'),
	url(r'^forum/(?P<forum_id>\d+)/(?P<page>\d+)/$', 'forum_view', name='forum_view_paged'),
	(r'^topic/(?P<topic_id>\d+)/$', 'topic_view'),
	(r'^topic/(?P<topic_id>\d+)/(?P<page>\d+)/$', 'topic_view'),
	(r'^topic/new/(?P<forum_id>\d+)/$', 'topic_new'),
	(r'^post/(?P<post_id>\d+)/$', 'post_view'),
)