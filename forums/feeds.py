from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.contrib.syndication.views import Feed
from django.db.models import F
from forums.models import Forum, Topic, Post
from utils.annoying.functions import get_config


class ForumIndexFeed(Feed):
	title = "Latest posts in %s Forum" % get_config('SITE_NAME', "Trinitee")
	link = '/forum/'
	description = ""

	def items(self):
		posts = cache.get('forums_feed_topics')
		if posts == None:
			posts = list(Post.objects.filter(topic__first_post__id=F('id')) \
				.order_by('-created_at') \
				.select_related()[:get_config('FEED_ITEMS_PER_PAGE', 10)])
			cache.set('forums_feed_topics', posts)
		return posts

	def item_title(self, item):
		return item.topic.title

	def item_description(self, item):
		return item.content_html

	def item_pubdate(self, item):
		return item.created_at


class ForumFeed(Feed):
	description = ""

	def get_object(self, request, forum_id):
		return get_object_or_404(Forum, pk=forum_id)

	def title(self, item):
		return "Latest posts in forum \"%s\" - %s" % (item.name, get_config('SITE_NAME', "Trinitee"))

	def link(self, item):
		return item.get_absolute_url()

	def items(self, item):
		posts = cache.get('forums_feed_forum_%s' % item)
		if posts == None:
			posts = list(Post.objects.filter(topic__forum=item) \
				.order_by('-created_at') \
				.select_related()[:get_config('FEED_ITEMS_PER_PAGE', 10)])
			cache.set('forums_feed_forum_%s' % item, posts)
		return posts

	def item_title(self, item):
		return item.topic.title

	def item_description(self, item):
		return item.content_html

	def item_pubdate(self, item):
		return item.created_at


class TopicFeed(Feed):
	description = ""

	def get_object(self, request, topic_id):
		return get_object_or_404(Topic, pk=topic_id)

	def title(self, item):
		return "Latest posts in topic \"%s\" - %s" % (item.title, get_config('SITE_NAME', "Trinitee"))

	def link(self, item):
		return item.get_absolute_url()

	def items(self, item):
		posts = cache.get('forums_feed_topic_%s' % item)
		if posts == None:
			posts = list(Post.objects.filter(topic=item) \
				.order_by('-created_at') \
				.select_related()[:get_config('FEED_ITEMS_PER_PAGE', 10)])
			cache.set('forums_feed_topic_%s' % item, posts)
		return posts

	def item_title(self, item):
		return item.topic.title

	def item_description(self, item):
		return item.content_html

	def item_pubdate(self, item):
		return item.created_at


class UserPostsFeed(Feed):
	description = ""

	def get_object(self, request, user_id):
		return get_object_or_404(User, pk=user_id)

	def title(self, item):
		return "Latest posts of user \"%s\" - %s" % (item.username, get_config('SITE_NAME', "Trinitee"))

	def link(self, item):
		return item.get_absolute_url()

	def items(self, item):
		posts = cache.get('forums_feed_user_%s' % item)
		if posts == None:
			posts = list(Post.objects.filter(author=item) \
				.order_by('-created_at') \
				.select_related()[:get_config('FEED_ITEMS_PER_PAGE', 10)])
			cache.set('forums_feed_user_%s' % item, posts)
		return posts

	def item_title(self, item):
		return item.topic.title

	def item_description(self, item):
		return item.content_html

	def item_pubdate(self, item):
		return item.created_at
