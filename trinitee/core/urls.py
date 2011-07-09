from django.conf.urls.defaults import include, patterns, url

urlpatterns = patterns('',
	(r'^permissions/', include('core.perms.urls')),
)