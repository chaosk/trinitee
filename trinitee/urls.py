from django.conf.urls.defaults import patterns, url, include, handler404, handler500
from django.contrib import admin
import settings

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'django.views.generic.simple.direct_to_template',
		{'template': 'home.html'}, name='home'),
	(r'^accounts/', include('userena.urls')),
	(r'^forums/', include('forums.urls')),
	(r'^wiki/', include('wiki.urls')),
	(r'^messages/', include('userena.contrib.umessages.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^', include('core.urls')),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve',
			{'document_root': settings.MEDIA_ROOT}),
	)
