from django.conf.urls.defaults import *

urlpatterns = patterns('trinitee.accounts.views',
	(r'^profile/$', 'profile_index'),
	(r'^edit/$', 'profile_edit'),
	(r'^login/$', 'login_'),
	(r'^logout/$', 'logout_'),
	(r'^new/$', 'register'),
	(r'^activation/(?P<user_id>)\d+/(?P<activation_key>)\w+/$', 'activation'),
)

urlpatterns += patterns('django.contrib.auth.views',
	(r'^password_reset/$', 'password_reset', {'template_name':
		'accounts/password_reset.html',
		'email_template_name': 'accounts/email/password_reset.html'}),
	(r'^password_reset/done$', 'password_reset_done', {'template_name':
		'accounts/password_reset_done.html',
		'email_template_name': 'accounts/email/password_reset.html'}),
)