from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from utils.ordering.urls import urlpatterns as ordering_urlpatterns
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'home.views.homepage', name='home'),
	(r'^forum/', include('forums.urls')),
	(r'^user/', include('accounts.urls')),
	(r'^users/', 'accounts.views.userlist'),
	(r'^profile/(?P<user_id>\d+)/$',
		'accounts.views.profile_details'),
	(r'^static/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root': settings.MEDIA_ROOT}),
	url(r'^downloads/$', 'downloads.views.downloads', name='downloads'),
	(r'^grappelli/', include('grappelli.urls')),
	(r'^admin_tools/', include('admin_tools.urls')),
	(r'^admin/', include(admin.site.urls)),
)

urlpatterns += ordering_urlpatterns