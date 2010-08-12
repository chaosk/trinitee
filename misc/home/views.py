from django.core.cache import cache
from django.db.models import F
from downloads.models import Release
from forums.models import Post
from utilities.annoying.functions import get_config, get_object_or_None
from utilities.annoying.decorators import render_to
from utilities.httpagentparser import os_detect


@render_to('misc/home/homepage.html')
def homepage(request):
	os, flavor = os_detect(request.META['HTTP_USER_AGENT'])
	flavor = '_' + flavor if flavor else ''
	latest_download = cache.get('homepage_latest_download_%s%s' % (os, flavor))
	if latest_download == None:
		latest_download = get_object_or_None(Release.objects.select_related(),
			platform__name='%s%s' % (os, flavor))
		cache.set('homepage_latest_download_%s%s' % (os, flavor),
			latest_download, 86400)
	news_forum_id = get_config('NEWS_FORUM', 1)
	news = cache.get('homepage_news')
	if news == None:
		news = list(Post.objects.filter(topic__forum=news_forum_id,
			topic__first_post__id=F('id')).order_by('-created_at'). \
				select_related()[:get_config('NEWS_ITEMS_ON_HOMEPAGE', 5)])
		cache.set('homepage_news', news)
	journal_forum_id = get_config('JOURNAL_FORUM', 2)
	journal = cache.get('homepage_journal')
	if journal == None:
		journal = list(Post.objects.filter(topic__forum=journal_forum_id,
			topic__first_post__id=F('id')).order_by('-created_at'). \
				select_related()[:get_config('JOURNAL_ITEMS_ON_HOMEPAGE', 5)])
		cache.set('homepage_journal', journal)
	return {'news': news, 'journal': journal, 'forum_id': news_forum_id,
		'latest_download': latest_download}
