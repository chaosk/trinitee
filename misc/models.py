import datetime
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from misc.validators import expires_at_validator, mask_validator
from utilities import postmarkup
from utilities.annoying.functions import get_config


class Drawboard(models.Model):
	last_modified_at = models.DateTimeField(auto_now=True)
	last_modified_by = models.ForeignKey(User, blank=True, null=True)
	content = models.TextField(blank=True)
	content_html = models.TextField(blank=True)

	def save(self, *args, **kwargs):
		cache.delete('misc_drawboard')
		if get_config('ENABLE_BBCODE', False):
			markup = postmarkup.create(annotate_links=False,
				use_pygments=get_config('BBCODE_USE_PYGMENTS', False))
			self.content_html = markup(self.content)
		else:
			self.content_html = self.content
		super(Drawboard, self).save(*args, **kwargs)
		cache.set('misc_drawboard', self)


class Ban(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, related_name='bans_created')
	modified_at = models.DateTimeField(auto_now=True)
	modified_by = models.ForeignKey(User, blank=True, null=True,
		related_name='bans_modified')
	# Please note it's CharField, not an IPAddressField
	banned_mask = models.CharField(max_length=50, blank=True,
		validators=[mask_validator])
	banned_user = models.ForeignKey(User, blank=True, null=True,
		related_name='bans_applied')
	expires_at = models.DateTimeField(blank=True,
		default=datetime.datetime.today, validators=[expires_at_validator])
	comment = models.CharField(max_length=255, blank=True)

	def __unicode__(self):
		return "%s / %s" % (self.banned_user.username if self.banned_user else '-',
			self.banned_mask if self.banned_mask else '-')

	def save(self, *args, **kwargs):
		cache.delete('misc_bans')
		super(Ban, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		cache.delete('misc_bans')
		super(Ban, self).delete(*args, **kwargs)

	def clean(self):
		if not self.banned_mask and not self.banned_user:
			raise ValidationError("You have to provide mask and/or user to ban.")


class StoredNotification(models.Model):
# This was made, because new message framework
# doesn't support offline notifications by itself.
	user = models.ForeignKey(User)
	message = models.TextField()
	level = models.PositiveIntegerField(default=20)
	created_at = models.DateTimeField(auto_now_add=True)


class WarningReason(models.Model):
# List of people I hate for this one:
#  - chi1
	reason = models.CharField(max_length=30)

	def __unicode__(self):
		return self.reason
