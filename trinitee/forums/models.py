from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
	title = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	parent = models.ForeignKey('self', blank=True, null=True)
	ordering = models.IntegerField(default=1)

	def __unicode__(self):
		return self.title


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
	first_post = models.OneToOneField('Post', related_name='topic_root')

	def __unicode__(self):
		return self.title


class Post(models.Model):
	topic = models.ForeignKey('Topic')
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, related_name='created_posts')
	modified_at = models.DateTimeField(auto_now=True)
	modified_by = models.ForeignKey(User, blank=True, null=True,
		related_name='modified_posts')
	show_edits = models.BooleanField(default=True)
	content = models.TextField()
	content_html = models.TextField()

	def __unicode__(self):
		return "#{0} by {1}".format(self.id, self.created_by)


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
