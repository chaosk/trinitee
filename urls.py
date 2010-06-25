from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from forums.feeds import ForumIndexFeed, ForumFeed, TopicFeed
from home.feeds import NewsFeed, JournalFeed
from utils.ordering.urls import urlpatterns as ordering_urlpatterns
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'home.views.homepage', name='home'),
	(r'^forum/', include('forums.urls')),
	(r'^user/', include('accounts.urls')),
	(r'^users/', 'accounts.views.userlist'),
	(r'^profile/(?P<user_id>\d+)/$',
		'accounts.views.profile_details'),

	url(r'^feed/$', NewsFeed(), name='feed_news'),
	url(r'^feed/journal/$', JournalFeed(), name='feed_journal'),
	url(r'^feed/forums/$', ForumIndexFeed(), name='feed_forums_index'),
	url(r'^feed/forums/(?P<forum_id>\d+)/$', ForumFeed(), name='feed_forums_forum'),
	url(r'^feed/forums/topic/(?P<topic_id>\d+)/$', TopicFeed(), name='feed_forums_topic'),
	url(r'^feed/forums/userposts/(?P<user_id>\d+)/$', TopicFeed(), name='feed_forums_user'),

	(r'^static/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root': settings.MEDIA_ROOT}),
	url(r'^downloads/$', 'downloads.views.downloads', name='downloads'),
	(r'^grappelli/', include('grappelli.urls')),
	(r'^admin_tools/', include('admin_tools.urls')),
	(r'^admin/', include(admin.site.urls)),
)

urlpatterns += ordering_urlpatterns