from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# FIXME
handler404 = '___.views.404'
handler500 = '___.views.500'

urlpatterns = patterns('',
	(r'^$', 'django.views.generic.simple.direct_to_template',
		{'template': 'index.html'}),
	(r'^forum/', include('trinitee.forums.urls')),
	(r'^user/', include('trinitee.accounts.urls')),
	(r'^profile/(?P<user_id>\d+)/$',
		'trinitee.accounts.views.profile_details'),
	#(r'$', '___.views.homepage'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
