from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from forums.feeds import ForumIndexFeed, ForumFeed, TopicFeed, AdminReportFeed
from home.feeds import NewsFeed, JournalFeed
from utilities.ordering.urls import urlpatterns as ordering_urlpatterns
from utilities.dajaxice.core import dajaxice_autodiscover
admin.autodiscover()
dajaxice_autodiscover()

feeds = {
	'reports': AdminReportFeed,
}

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
	(r'^feed/secured/(?P<url>.*)/$', 'forums.feeds.feed', {'feed_dict': feeds}),
	(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
		{'feed_dict': feeds}),

	(r'^static/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root': settings.MEDIA_ROOT}),
	url(r'^downloads/$', 'downloads.views.downloads', name='downloads'),
	(r'^grappelli/', include('utilities.grappelli.urls')),
	(r'^admin_tools/', include('utilities.admin_tools.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('utilities.dajaxice.urls'))
)

urlpatterns += ordering_urlpatterns