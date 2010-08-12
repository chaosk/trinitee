from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from accounts.models import Group
from utilities import postmarkup
from utilities.annoying.fields import AutoOneToOneField, JSONField
from utilities.annoying.functions import get_config
from utilities.ordering.models import OrderedModel


class Post(models.Model):
	topic = models.ForeignKey('Topic', related_name='posts')
	created_at = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(User, related_name='posts')
	author_ip = models.IPAddressField()
	modified_at = models.DateTimeField(auto_now=True)
	modified_by = models.ForeignKey(User, blank=True, null=True,
		related_name='modified_by')
	content = models.TextField()
	content_html = models.TextField()

	class Meta:
		ordering = ['created_at']
		get_latest_by = 'created_at'

	def __unicode__(self):
		return "Post #%s by %s" % (self.id, self.author)

	def save(self, *args, **kwargs):
		if get_config('ENABLE_BBCODE', False):
			markup = postmarkup.create(annotate_links=False,
				use_pygments=get_config('BBCODE_USE_PYGMENTS', False))
			self.content_html = markup(self.content)
		else:
			self.content_html = self.content
		super(Post, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self_id = self.id
		topic = self.topic
		forum = topic.forum
		topic_first_post_id = topic.first_post.id
		topic_last_post_id = topic.last_post.id
		self.last_topic_post.clear()
		self.last_forum_post.clear()
		PostKarma.objects.filter(post=self).delete()
		super(Post, self).delete(*args, **kwargs)
		# if post was first in topic - remove topic
		if self_id == topic_first_post_id:
			topic.delete()
		else:
			topic.post_count -= 1
			if self_id == topic_last_post_id:
				topic.last_post = topic.get_last_post()
				if self_id == forum.last_post.id:
					forum.last_post = forum.get_last_post()
			topic.save()
			cache.delete('forums_topic_%s' % topic.id)
		forum.post_count -= 1
		forum.save()
		cache.delete('forums_forum_%s' % forum.id)
		cache.delete('forums_count_posts')

	@models.permalink
	def get_absolute_url(self):
		return ('forums.views.post_permalink', (), {'post_id': self.id})

	def get_karma(self, force_refresh=False):
	# FIXME add bulk retrieving PLX PLX PLX.
	# My butt hurts.
	#                      --- Your database
		karma = cache.get('forums_karma_%s' % self.id)
		if force_refresh or karma == None:
			try:
				karma = sum(PostKarma.objects.filter(post__exact=self). \
					values_list('karma', flat=True))
			except IndexError:
				karma = 0
			cache.set('forums_karma_%s' % self.id, karma)
		return karma


class Topic(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(User, related_name='topics')
	title = models.CharField(max_length=60)
	forum = models.ForeignKey('Forum', related_name='topics')
	view_count = models.IntegerField(blank=True, default=0)
	is_sticky = models.BooleanField(default=False)
	is_closed = models.BooleanField(default=False)

	first_post = models.ForeignKey('Post', related_name='first_topic_post',
		blank=True, null=True)
	last_post = models.ForeignKey('Post', related_name='last_topic_post',
		blank=True, null=True)
	post_count = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ['-created_at']
		get_latest_by = 'created_at'

	def __unicode__(self):
		return self.title

	def delete(self, *args, **kwargs):
		self.forum.update(post_count=F('post_count') - self.post_count,
			topic_count=F('topic_count') - 1)
		cache.delete('forums_topic_%s' % self.id)
		cache.delete('forums_forum_%s' % self.forum.id)
		super(Topic, self).delete(*args, **kwargs)
		cache.delete('forums_count_posts')
		cache.delete('forums_count_topics')

	@models.permalink
	def get_absolute_url(self):
		return ('forums.views.topic_view', (), {'topic_id': self.id})

	def get_post_count(self):
		return Post.objects.filter(topic__exact=self).count()

	def get_last_post(self):
		try:
			return Post.objects.filter(topic__exact=self).latest()
		except Post.DoesNotExist:
			return None

	def update_read(self, user):
		tracking = user.posttracking
		if tracking.last_read and (tracking.last_read > self.last_post.created_at):
			return
		if isinstance(tracking.topics, dict):
			if len(tracking.topics) > 5120:
				tracking.topics = None
				tracking.save()
			if self.last_post.id > tracking.topics.get(str(self.id), 0):
				tracking.topics[str(self.id)] = self.last_post.id
				tracking.save()
		else:
			tracking.topics = {self.id: self.last_post.id}
			tracking.save()


class Forum(OrderedModel):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True)
	category = models.ForeignKey('Category')
	can_read = models.ManyToManyField('accounts.Group', blank=True,
		related_name='forum_can_read')
	can_post_topic = models.ManyToManyField('accounts.Group', blank=True,
		related_name='forum_can_post_topic')
	can_post_reply = models.ManyToManyField('accounts.Group', blank=True,
		related_name='forum_can_post_reply')

	last_post = models.ForeignKey('Post', related_name='last_forum_post',
		blank=True, null=True)

	class Meta:
		ordering = ['category', 'order', 'name']
		verbose_name_plural = ('Forums')

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('forums.views.forum_view', (), {'forum_id': self.id})

	def get_post_count(self):
		return Post.objects.filter(topic__forum__exact=self).count()
	post_count = models.PositiveIntegerField(default=0)

	def get_topic_count(self):
		return Topic.objects.filter(forum__exact=self).count()
	topic_count = models.PositiveIntegerField(default=0)

	def get_last_post(self):
		try:
			return Post.objects.filter(topic__forum=self).latest()
		except Post.DoesNotExist:
			return None


class Category(OrderedModel):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ['order', 'name']
		verbose_name_plural = ('Categories')

	def __unicode__(self):
		return self.name


class PostTracking(models.Model):
	user = AutoOneToOneField(User, primary_key=True, related_name='post_tracking')
	topics = JSONField(null=True)
	last_read = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Post tracking'
		verbose_name_plural = 'Post tracking'


class PostKarma(models.Model):
	user = models.ForeignKey(User, related_name='karma')
	post = models.ForeignKey('Post', related_name='karma')
	KARMA_CHOICES = (
		(1, 'PLUS'),
		(-1, 'MINUS'),
	)
	karma = models.IntegerField(choices=KARMA_CHOICES, default=0)

	class Meta:
		unique_together = ('user', 'post')

	def __unicode__(self):
		return "%s" % self.karma


class Report(models.Model):
	post = models.ForeignKey('Post')
	reported_by = models.ForeignKey(User, related_name='reports')
	reported_at = models.DateTimeField(auto_now_add=True)
	content = models.CharField(max_length=255)
	reviewed_by = models.ForeignKey(User, blank=True, null=True,
		related_name='reviewed_reports')
	reviewed_at = models.DateTimeField(auto_now=True)
	status = models.NullBooleanField(default=None)

	def __unicode__(self):
		return "Report %d" % self.id

	def change_list_status(self):
		""" Workaround for http://code.djangoproject.com/ticket/11058 """
		pass


def post_post_save(instance, **kwargs):
	post = instance
	topic = post.topic
	forum = topic.forum
	if kwargs['created']:
		if topic.post_count == 0:
			topic.first_post = post
		topic.last_post = post
		topic.post_count = topic.get_post_count()
		forum.last_post = post
		forum.post_count = forum.get_post_count()
		profile = post.author.profile
		profile.post_count = profile.get_post_count()
		profile.save(force_update=True)
		topic.save(force_update=True)
		forum.save(force_update=True)
		cache.delete('forums_count_posts')
	cache.delete('forums_topics_%s' % forum.id)
	cache.delete('forums_posts_%s' % topic.id)


def post_topic_save(instance, **kwargs):
	topic = instance
	forum = topic.forum
	if kwargs['created']:
		forum.topic_count = forum.get_topic_count()
		forum.save(force_update=True)
		cache.delete('homepage_news')
		cache.delete('forums_count_topics')
	cache.delete('forums_topics_%s' % forum)
	cache.delete('forums_posts_%s' % topic)


post_save.connect(post_post_save, sender=Post)
post_save.connect(post_topic_save, sender=Topic)
