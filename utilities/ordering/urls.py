from django.conf.urls.defaults import *

urlpatterns = patterns('',
	url(r'^admin/orderedmove/(?P<direction>up|down)/(?P<model_type_id>\d+)/(?P<model_id>\d+)/$', 'utilities.ordering.views.admin_move_ordered_model', name="admin-move"),
)
