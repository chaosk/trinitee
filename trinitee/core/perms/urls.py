from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('core.perms.views',
	url(r'^(?P<contenttype_id>\d+)/$',
		'perms_detail', name='perms_detail'),
	url(r'^(?P<contenttype_id>\d+)/(?P<object_id>\d+)/$',
		'granular_perms_detail', name='granular_perms_detail'),
	url(r'^(?P<target_ct_id>\d+)/'
		'edit/(?P<actor_type>\w+)/(?P<actor_obj_id>[\d-]+)/$',
		'perms_edit', {'target_obj_id': None}, name='perms_edit'),
	url(r'^(?P<target_ct_id>\d+)/(?P<target_obj_id>\d+)/'
		'edit/(?P<actor_type>\w+)/(?P<actor_obj_id>[\d-]+)/$',
		'perms_edit', name='perms_edit'),
)