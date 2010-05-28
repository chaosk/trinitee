import datetime
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
	topic_id = models.ForeignKey('Topic')
	created_at = models.DateTimeField(auto_now_add=datetime.datetime.now)
	modified_at = models.DateField(auto_now=datetime.datetime.now)
	author = models.ForeignKey(User)
	content = models.TextField()

	class Meta:
		ordering = ('')
		get_latest_by = ''
		verbose_name_plural = ('Posts')

	def __unicode__(self):
		return "%s by %s" % (self.id, self.author)
	
	def get_absolute_url(self):
		return (forums.views.post_view, [str(self.id)])

class Topic(models.Model):
	created_at = models.DateTimeField(auto_now_add=datetime.datetime.now)
	subject = models.CharField(max_length=100)
	category = models.ForeignKey('Category')
	post_count = models.IntegerField(blank=True, null=True)
	is_sticky = models.BooleanField(default=False)
	is_closed = models.BooleanField(default=False)
	
	class Meta:
		ordering = ('')
		get_latest_by = ''
		verbose_name_plural = ('Topics')

	def __unicode__(self):
		return self.subject
	
	def get_absolute_url(self):
		return (forums.views.topic_view, [str(self.id)])

class Category(models.Model):
	category_name = models.CharField(max_length=100)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ('')
		get_latest_by = ''
		verbose_name_plural = ('Categories')

	def __unicode__(self):
		return self.category_name
	
	def get_absolute_url(self):
		return (forums.views.category_view, [str(self.id)])
