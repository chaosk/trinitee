from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views',
	(r'^settings/$', 'profile_settings'),
	(r'^settings/avatar/$', 'profile_settings_avatar'),
	(r'^settings/display/$', 'profile_settings_display'),
	(r'^settings/identity/$', 'profile_settings_identity'),
	(r'^settings/signature/$', 'profile_settings_signature'),
	(r'^login/$', 'login'),
	(r'^logout/$', 'logout'),
	(r'^register/$', 'register'),
	(r'^activate/(?P<user_id>\d+)/(?P<activation_key>\w+)/$', 'activate_account'),
	(r'^activate/resend/$', 'resend_activation_key'),
)

urlpatterns += patterns('django.contrib.auth.views',
	(r'^password_reset/$', 'password_reset', {'template_name':
		'accounts/password_reset.html',
		'email_template_name': 'accounts/email/password_reset.html'}),
	(r'^password_reset/done/$', 'password_reset_done', {'template_name':
		'accounts/password_reset_done.html'}),
	(r'^password_reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', {'template_name':
		'accounts/password_reset_confirm.html'}),
	(r'^password_reset/complete/$', 'password_reset_complete', {'template_name':
		'accounts/password_reset_complete.html'}),
)
