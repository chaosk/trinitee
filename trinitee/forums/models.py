from django.contrib.auth.models import User
from django.db import models
from core.perms.models import GranularPermissionedModel
from markdown import markdown


class Category(GranularPermissionedModel):
	title = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	parent = models.ForeignKey('self', blank=True, null=True,
		related_name='categories')
	ordering = models.IntegerField(default=1)

	class Meta:
		verbose_name_plural = "Categories"
		permissions = (
			('view_category', 'Can view category'),
			('add_topics_category', 'Can create new topics in category'),
			('add_posts_category', 'Can create new posts in category'),
			('moderate_category', 'Can moderate category'),
		)

	def __unicode__(self):
		return self.title

	@models.permalink
	def get_absolute_url(self):
		return ('forums.views.topic_list', (), {'category_id': self.id})


class Topic(models.Model):
	title = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, related_name='created_topics')
	modified_at = models.DateTimeField(auto_now=True)
	modified_by = models.ForeignKey(User, blank=True, null=True,
		related_name='modified_topics')
	category = models.ForeignKey('Category')
	is_closed = models.BooleanField(default=False)
	is_sticky = models.BooleanField(default=False)

	@property
	def first_post(self):
		try:
			return self.posts[0]
		except IndexError:
			return None

	@property
	def last_post(self):
		try:
			return self.posts.order_by('-created_at')[0]
		except IndexError:
			return None
	
	@property
	def post_count(self):
		return self.posts.count()

	def __unicode__(self):
		return self.title

	@models.permalink
	def get_absolute_url(self):
		return ('forums.views.topic_detail', (),
			{'category_id': self.category_id, 'topic_id': self.id})


class Post(models.Model):
	topic = models.ForeignKey('Topic', related_name='posts')
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, related_name='created_posts')
	modified_at = models.DateTimeField(auto_now=True)
	modified_by = models.ForeignKey(User, blank=True, null=True,
		related_name='modified_posts')
	show_edits = models.BooleanField(default=True)
	content = models.TextField()
	content_html = models.TextField()

	def save(self, *args, **kwargs):
		self.content_html = markdown(self.content)
		super(Post, self).save(*args, **kwargs)

	def __unicode__(self):
		return "#{0} by {1}".format(self.id, self.created_by)

	@models.permalink
	def get_absolute_url(self):
		# make it a real permalink
		return ('forums.views.post_permalink', (), {'post_id': self.id})


class PostKarma(models.Model):
	user = models.ForeignKey(User)
	post = models.ForeignKey(Post)

	KARMA_NEGATIVE = -1
	KARMA_NEUTRAL = 0
	KARMA_POSITIVE = 1
	KARMA_CHOICES = (
		(KARMA_NEGATIVE, "Negative"),
		(KARMA_NEUTRAL, "Neutral"),
		(KARMA_POSITIVE, "Positive"),
	)	
	karma = models.IntegerField(choices=KARMA_CHOICES, default=KARMA_NEUTRAL)

	class Meta:
		unique_together = ('user', 'post')

	def __unicode__(self):
		return "{0}, {1} to {2} for #{3}".format(
			self.get_karma_display(), self.user,
			self.post.created_by, self.post.id
		)


class Poll(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, related_name='polls_started')
	expires_at = models.DateTimeField(blank=True, null=True)
	question = models.CharField(max_length=255)
	topic = models.ForeignKey(Topic)
	max_votes = models.PositiveIntegerField(default=1,
		help_text="Number of choices user can pick.")


class Choice(models.Model):
	poll = models.ForeignKey(Poll)
	choice = models.CharField(max_length=255)


class Vote(models.Model):
	poll = models.ForeignKey(Poll)
	choice = models.ForeignKey(Choice)
	user = models.ForeignKey(User)

	class Meta:
		unique_together = ('poll', 'choice', 'user')
