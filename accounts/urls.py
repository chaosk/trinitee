from django.conf.urls.defaults import *

urlpatterns = patterns('trinitee.accounts.views',
	(r'^profile/$', 'profile_index'),
	(r'^edit/$', 'profile_edit'),
	(r'^login/$', 'login_'),
	(r'^logout/$', 'logout_'),
	(r'^new/$', 'register'),
)

urlpatterns += patterns('django.contrib.auth.views',
	(r'^password_reset/$', 'password_reset', {'template_name': 'accounts/password_reset.html'}),
)