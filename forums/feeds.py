from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.contrib.syndication.views import feed as unauthenticated_feed
from django.contrib.syndication.feeds import Feed as DeprecatedFeed
from django.contrib.syndication.views import Feed
from django.db.models import F
from forums.models import Forum, Topic, Post, Report
from utilities.annoying.functions import get_config
from utilities.internal.decorators import user_passes_test_or_basicauth


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


class AdminReportFeed(DeprecatedFeed):
	title = "Unreviewed user reports - %s Forum" % get_config('SITE_NAME', "Trinitee")
	link = '/admin/forums/report/'

	def items(self):
		reports = cache.get('admin_forums_feed_reports')
		if reports == None:
			reports = list(Report.objects.filter(status=None)[:get_config('FEED_ITEMS_PER_PAGE', 10)])
			cache.set('admin_forums_feed_reports', reports)
		return reports

	def item_link(self, item):
		return "/admin/forums/report/%s" % item.id

	def item_title(self, item):
		title = "Report %d from %s" % (item.id, item.reported_by)
		return title

	def item_description(self, item):
		return "%s<br /><br /><a href=\"%s\">Reported post</a> (by %s):<br />%s<br />" % \
			(item.content, item.post.get_absolute_url(), item.post.author, item.post.content)

	def item_pubdate(self, item):
		return item.reported_at


@user_passes_test_or_basicauth(lambda u: u.is_staff or u.is_superuser, 'Trinitee')
def feed(request, url, feed_dict=None):
    return unauthenticated_feed(request, url, feed_dict)