from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'django.views.generic.simple.direct_to_template',
		{'template': 'index.html'}, name='home'),
	(r'^forum/', include('trinitee.forums.urls')),
	(r'^user/', include('trinitee.accounts.urls')),
	(r'^users/', 'accounts.views.userlist'),
	(r'^profile/(?P<user_id>\d+)/$',
		'accounts.views.profile_details'),
	(r'^static/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root': settings.MEDIA_ROOT}),
	#(r'$', '___.views.homepage'),
	(r'^grappelli/', include('grappelli.urls')),
	(r'^admin/', include(admin.site.urls)),
)
