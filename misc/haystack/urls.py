from django.conf.urls.defaults import *
from forums.models import Topic
from misc.haystack.forms import PostSearchForm
from misc.haystack.views import PostSearchView
from haystack.query import SearchQuerySet


urlpatterns = patterns('haystack.views',
	url(r'^forum/$', PostSearchView(
		template='search/forum_search.html',
		form_class=PostSearchForm,
		searchqueryset=SearchQuerySet().models(Topic)
	), name='forum_search'),
)
