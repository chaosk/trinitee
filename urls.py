from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from forums.feeds import (ForumIndexFeed, ForumFeed, TopicFeed,
	UserPostsFeed, AdminReportFeed)
from misc.home.feeds import NewsFeed, JournalFeed
from utilities.ordering.urls import urlpatterns as ordering_urlpatterns
from utilities.dajaxice.core import dajaxice_autodiscover
import haystack.urls
admin.autodiscover()
dajaxice_autodiscover()

feeds = {
	'reports': AdminReportFeed,
}

handler500 = 'misc.views.server_error'

urlpatterns = patterns('',
	url(r'^$', 'misc.home.views.homepage', name='home'),
	url(r'^blog/$', 'misc.home.views.journal', name='journal'),
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
	url(r'^feed/forums/userposts/(?P<user_id>\d+)/$', UserPostsFeed(), name='feed_forums_user'),
	(r'^feed/secured/(?P<url>.*)/$', 'forums.feeds.feed', {'feed_dict': feeds}),
	(r'^random/$', 'django.views.generic.simple.direct_to_template', {'template': 'misc/random.html'}),
	url(r'^downloads/$', 'downloads.views.downloads', name='downloads'),
	(r'^grappelli/', include('utilities.grappelli.urls')),
	(r'^admin_tools/', include('utilities.admin_tools.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('utilities.dajaxice.urls')),
	(r'^', include('utilities.superflatpages.urls')),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^403/$', 'django.views.generic.simple.direct_to_template', {'template': '403.html'}),
		(r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
		(r'^500/$', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),
		(r'^503/$', 'django.views.generic.simple.direct_to_template', {'template': '503.html'}),
		(r'^ban/$', 'django.views.generic.simple.direct_to_template', {'template': 'misc/banned.html'}),
		(r'^static/(?P<path>.*)$', 'django.views.static.serve',
			{'document_root': settings.MEDIA_ROOT}),
	)

urlpatterns += ordering_urlpatterns