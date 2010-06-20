from django.db.models import F
from forums.models import Post
from utils.annoying.functions import get_config, get_object_or_None
from utils.annoying.decorators import render_to
from utils.httpagentparser import os_detect

@render_to('home/homepage.html')
def homepage(request):
	# os, flavor = os_detect(request.META['HTTP_USER_AGENT'])
	# latest_download = get_object_or_None(Release, platform=os, flavor=flavor)
	news_forum_id = get_config('NEWS_FORUM', 1)
	news = Post.objects.filter(topic__forum=news_forum_id,
		topic__first_post__id=F('id')).order_by('-created_at'). \
			select_related()[:get_config('NEWS_ITEMS_ON_HOMEPAGE', 5)]
	return {'news': news, 'forum_id': news_forum_id }#, 'latest_download': latest_download}