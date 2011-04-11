from django.conf.urls.defaults import *

urlpatterns = patterns('community_content.views',
	(r'^$', 'index'),
)