import datetime
from django.db import models
from django.contrib.auth.models import User
from utils.annoying.fields import AutoOneToOneField, JSONField
from utils.annoying.functions import get_config

class Post(models.Model):
	topic = models.ForeignKey('Topic')
	created_at = models.DateTimeField(auto_now_add=datetime.datetime.now)
	author = models.ForeignKey(User, related_name='author')
	modified_at = models.DateTimeField(auto_now=datetime.datetime.now)
	modified_by = models.ForeignKey(User, blank=True, null=True,
		related_name='modified_by')
	content = models.TextField()
	content_html = models.TextField()

	def save(self, *args, **kwargs):
		if get_config('ENABLE_BBCODE', False):
			self.content_html = utils.bbcode(self.content)
		if get_config('ENABLE_SMILEYS', False):
			self.content = utils.smileys(self.content_html)
		super(Post, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self_id = self.id
		topic = self.topic
		topic_first_post_id = topic.first_post.id
		super(Post, self).delete(*args, **kwargs)
		# if post was first in topic - remove topic
		if self_id == topic_first_post_id:
			topic.delete()

	class Meta:
		ordering = ['created_at']
		get_latest_by = 'created_at'
		verbose_name_plural = ('Posts')

	def __unicode__(self):
		return "%s by %s" % (self.id, self.author)
	
	def get_absolute_url(self):
		return "/forum/post/%s" % str(self.id)

class Topic(models.Model):
	created_at = models.DateTimeField(auto_now_add=datetime.datetime.now)
	title = models.CharField(max_length=100)
	forum = models.ForeignKey('Forum')
	post_count = models.IntegerField(blank=True, null=True)
	view_count = models.IntegerField(blank=True, default=0)
	is_sticky = models.BooleanField(default=False)
	is_closed = models.BooleanField(default=False)
	
	def _get_first_post(self):
		return Post.objects.filter(topic__exact=self).order_by('created_at')[0:1].get()
	first_post = property(_get_first_post)
	
	def _get_last_post(self):
		return Post.objects.filter(topic__exact=self).latest()
	last_post = property(_get_last_post)
	
	def _get_post_count(self):
		return Post.objects.filter(topic__exact=self).count()
	post_count = property(_get_post_count)
	
	class Meta:
		ordering = ['-is_sticky', '-created_at']
		get_latest_by = 'created_at'
		verbose_name_plural = ('Topics')

	def __unicode__(self):
		return self.title
	
	def get_absolute_url(self):
		return "/forum/topic/%s" % str(self.id)

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

class Forum(models.Model):
	name = models.CharField(max_length=100)
	ordering = models.PositiveIntegerField(default=1)
	description = models.TextField(blank=True)
	category = models.ForeignKey('Category')

	def _get_last_post(self):
		return Post.objects.filter(topic__forum__exact=self).latest('created_at')
	last_post = property(_get_last_post)

	def _get_post_count(self):
		return Post.objects.filter(topic__forum__exact=self).count()
	post_count = property(_get_post_count)

	def _get_topic_count(self):
		return Topic.objects.filter(forum__exact=self).count()
	topic_count = property(_get_topic_count)

	class Meta:
		ordering = ['-ordering', 'name']
		verbose_name_plural = ('Forums')

	def __unicode__(self):
		return self.name
	
	def get_absolute_url(self):
		return "/forum/%s" % str(self.id)

class Category(models.Model):
	name = models.CharField(max_length=100)
	ordering = models.PositiveIntegerField(default=1)
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