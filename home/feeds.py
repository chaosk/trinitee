from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed
from django.db.models import F
from forums.models import Topic, Post
from utils.annoying.functions import get_config


class NewsFeed(Feed):
	title = "%s News" % get_config('SITE_NAME', "Trinitee")
	link = '/'
	description = ""

	def items(self):
		news_forum_id = get_config('NEWS_FORUM', 1)
		news = cache.get('homepage_news')
		if news == None:
			news = list(Post.objects.filter(topic__forum=news_forum_id,
				topic__first_post__id=F('id')).order_by('-created_at'). \
					select_related()[:get_config('NEWS_ITEMS_ON_HOMEPAGE', 5)])
			cache.set('homepage_news', news)
		return news

	def item_title(self, item):
		return item.topic.title

	def item_description(self, item):
		return item.content_html

	def item_pubdate(self, item):
		return item.created_at


class JournalFeed(Feed):
	title = "Developer Journal - %s" % get_config('SITE_NAME', "Trinitee")
	link = '/journal/'
	description = ""

	def items(self):
		journal_forum_id = get_config('JOURNAL_FORUM', 2)
		entries = cache.get('homepage_journal')
		if entries == None:
			entries = list(Post.objects.filter(topic__forum=journal_forum_id,
				topic__first_post__id=F('id')).order_by('-created_at') \
				.select_related()[:get_config('NEWS_ITEMS_ON_HOMEPAGE', 5)])
			cache.set('homepage_journal', entries)
		return entries

	def item_title(self, item):
		return item.topic.title

	def item_description(self, item):
		return item.content_html

	def item_pubdate(self, item):
		return item.created_at
