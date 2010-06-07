from django.conf.urls.defaults import *

urlpatterns = patterns('trinitee.accounts.views',
	(r'^settings/$', 'profile_settings'),
	(r'^settings/avatar/$', 'profile_settings_avatar'),
	(r'^settings/display/$', 'profile_settings_display'),
	(r'^settings/identity/$', 'profile_settings_identity'),
	(r'^settings/signature/$', 'profile_settings_signature'),
	(r'^login/$', 'login_'),
	(r'^logout/$', 'logout_'),
	(r'^new/$', 'register'),
	(r'^activate/(?P<user_id>\d+)/(?P<activation_key>\w+)/$', 'activate_account'),
	(r'^activate/resend/(?P<user_id>\d+)/$', 'resend_activation_key'),
)

urlpatterns += patterns('django.contrib.auth.views',
	(r'^password_reset/$', 'password_reset', {'template_name':
		'accounts/password_reset.html',
		'email_template_name': 'accounts/email/password_reset.html'}),
	(r'^password_reset/done$', 'password_reset_done', {'template_name':
		'accounts/password_reset_done.html',
		'email_template_name': 'accounts/email/password_reset_done.html'}),
)