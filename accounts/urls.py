from django.conf.urls.defaults import *

urlpatterns = patterns('trinity.accounts.views',
	(r'^(?P<user_id>\d+)/$', 'profile_details'),
	(r'^new/$', 'register'),
)

urlpatterns += patterns('django.contrib.auth.views',
	(r'^login/$', 'login', { 'template_name': 'accounts/login.html' }),
	(r'^logout/$', 'logout', { 'template_name': 'accounts/logout.html' }),
	(r'^password_reset/$', 'password_reset', { 'template_name': 'accounts/password_reset.html' }),
)