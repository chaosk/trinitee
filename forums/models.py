import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from utils.annoying.fields import AutoOneToOneField, JSONField
from utils.annoying.functions import get_config
from utils import postmarkup


class Post(models.Model):
	topic = models.ForeignKey('Topic', related_name='posts')
	created_at = models.DateTimeField(auto_now_add=datetime.datetime.now)
	author = models.ForeignKey(User, related_name='posts')
	modified_at = models.DateTimeField(auto_now=datetime.datetime.now)
	modified_by = models.ForeignKey(User, blank=True, null=True,
		related_name='modified_by')
	content = models.TextField()
	content_html = models.TextField()

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
		self.last_topic_post.clear()
		self.last_forum_post.clear()
		super(Post, self).delete(*args, **kwargs)
		# if post was first in topic - remove topic
		if self_id == topic_first_post_id:
			topic.delete()
		else:
			topic.post_count -= 1
			topic.last_post = topic.get_last_post()
			topic.save()
		forum.last_post = forum.get_last_post()
		forum.post_count -= 1
		forum.save()

	class Meta:
		ordering = ['created_at']
		get_latest_by = 'created_at'
		verbose_name_plural = ('Posts')

	def __unicode__(self):
		return "%s by %s" % (self.id, self.author)

	def get_absolute_url(self):
		return reverse('forums.views.post_permalink',
			kwargs={'post_id': self.id})


class Topic(models.Model):
	created_at = models.DateTimeField(auto_now_add=datetime.datetime.now)
	author = models.ForeignKey(User, related_name='topics')
	title = models.CharField(max_length=100)
	forum = models.ForeignKey('Forum', related_name='topics')
	post_count = models.IntegerField(blank=True, null=True)
	view_count = models.IntegerField(blank=True, default=0)
	is_sticky = models.BooleanField(default=False)
	is_closed = models.BooleanField(default=False)

	last_post = models.ForeignKey('Post', related_name='last_topic_post',
		blank=True, null=True)

	def _get_first_post(self):
		return Post.objects.filter(topic__exact=self). \
			order_by('created_at')[0]
	first_post = property(_get_first_post)

	def get_post_count(self):
		return Post.objects.filter(topic__exact=self).count()
	post_count = models.PositiveIntegerField(default=0)

	def delete(self, *args, **kwargs):
		forum = self.forum
		# delete all posts belonging to this topic
		posts = Post.objects.filter(topic__id=self.id)
		count = posts.count()
		posts.delete()
		super(Topic, self).delete(*args, **kwargs)
		forum.post_count -= count
		forum.topic_count -= 1
		forum.save()

	class Meta:
		ordering = ['-is_sticky', '-created_at']
		get_latest_by = 'created_at'
		verbose_name_plural = ('Topics')

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('forums.views.topic_view',
			kwargs={'topic_id': self.id})

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

	def get_last_post(self):
		try:
			return Post.objects.filter(topic__exact=self).latest()
		except Post.DoesNotExist:
			return None


class Forum(models.Model):
	name = models.CharField(max_length=100)
	ordering = models.PositiveIntegerField(default=1)
	description = models.TextField(blank=True)
	category = models.ForeignKey('Category')

	last_post = models.ForeignKey('Post', related_name='last_forum_post',
		blank=True, null=True)

	def get_post_count(self):
		return Post.objects.filter(topic__forum__exact=self).count()
	post_count = models.PositiveIntegerField(default=0)

	def get_topic_count(self):
		return Topic.objects.filter(forum__exact=self).count()
	topic_count = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ['-ordering', 'name']
		verbose_name_plural = ('Forums')

	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('forums.views.forum_view',
			kwargs={'forum_id': self.id})

	def get_last_post(self):
		try:
			return Post.objects.filter(topic__forum=self).latest()
		except Post.DoesNotExist:
			return None


class Category(models.Model):
	name = models.CharField(max_length=100)
	ordering = models.PositiveIntegerField(default=0)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ['-ordering', 'name']
		verbose_name_plural = ('Categories')

	def __unicode__(self):
		return self.name


class PostTracking(models.Model):
	user = AutoOneToOneField(User, primary_key=True)
	topics = JSONField(null=True)
	last_read = models.DateTimeField(auto_now=datetime.datetime.now)

	class Meta:
		verbose_name = 'Post tracking'
		verbose_name_plural = 'Post tracking'


def post_saved(instance, **kwargs):
	if kwargs['created']:
		post = instance
		topic = post.topic
		topic.last_post = post
		topic.post_count = topic.get_post_count()
		forum = topic.forum
		forum.last_post = post
		forum.post_count = forum.get_post_count()
		profile = post.author.profile
		profile.post_count = profile.get_post_count()
		profile.save(force_update=True)
		topic.save(force_update=True)
		forum.save(force_update=True)


def topic_saved(instance, **kwargs):
	if kwargs['created']:
		topic = instance
		forum = topic.forum
		forum.topic_count = forum.get_topic_count()
		forum.save(force_update=True)

post_save.connect(post_saved, sender=Post)
post_save.connect(topic_saved, sender=Topic)
