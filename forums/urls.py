from django.conf.urls.defaults import *

urlpatterns = patterns('forums.views',
	(r'^$', 'index'),
	(r'^(?P<forum_id>\d+)/$', 'forum_view'),
	(r'^post/(?P<post_id>\d+)/', 'post_permalink'),
	(r'^topic/(?P<topic_id>\d+)/$', 'topic_view'),
	(r'^topic/(?P<topic_id>\d+)/(?P<page>\d+)/$', 'topic_view'),
	(r'^topic/new/(?P<forum_id>\d+)/$', 'topic_new'),
	(r'^topic/reply/(?P<topic_id>\d+)/$', 'post_new'),
	(r'^post/edit/(?P<post_id>\d+)/$', 'post_edit'),
	(r'^post/delete/(?P<post_id>\d+)/$', 'post_delete'),
	(r'^topic/reply/(?P<topic_id>\d+)/q/(?P<quoted_post_id>\d+)$', 'post_new'),
	(r'^topic/close/(?P<topic_id>\d+)/$', 'close_topic'),
	(r'^topic/open/(?P<topic_id>\d+)/$', 'open_topic'),
	(r'^topic/stick/(?P<topic_id>\d+)/$', 'stick_topic'),
	(r'^topic/unstick/(?P<topic_id>\d+)/$', 'unstick_topic'),
	(r'^topic/move/(?P<topic_id>\d+)/$', 'move_topic'),
)
