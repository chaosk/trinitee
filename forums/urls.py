from django.conf.urls.defaults import *

urlpatterns = patterns('trinitee.forums.views',
	(r'^$', 'index'),
	url(r'^(?P<forum_id>\d+)/$', 'forum_view', name='forum_view'),
	url(r'^(?P<forum_id>\d+)/(?P<page>\d+)/$', 'forum_view', name='forum_view_paged'),
	(r'^topic/(?P<topic_id>\d+)/$', 'topic_view'),
	(r'^topic/(?P<topic_id>\d+)/(?P<page>\d+)/$', 'topic_view'),
	(r'^topic/new/(?P<forum_id>\d+)/$', 'topic_new'),
	(r'^post/(?P<post_id>\d+)/$', 'post_view'),
	(r'^topic/reply/(?P<topic_id>\d+)/$', 'post_new'),
	(r'^topic/reply/(?P<topic_id>\d+)/q/(?P<quoted_post_id>\d+)$', 'post_new'),	
)