from django.conf.urls.defaults import *

urlpatterns = patterns('trinity.forums.views',
	(r'^$', 'index'),
	(r'^category/(?P<category_id>\d+)/$', 'category_view'),
	(r'^topic/(?P<topic_id>\d+)/$', 'topic_view'),
	(r'^post/(?P<post_id>\d+)/$', 'post_view'),
)