import datetime
from pytz import common_timezones
from django.contrib.auth.models import User, Group, Permission
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from forums.models import Post
from utils.annoying.functions import get_config

TIMEZONE_CHOICES = tuple([(tz, tz) for tz in common_timezones])

class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True)
	avatar = models.ForeignKey('Avatar', blank=True, null=True)
	signature = models.CharField(blank=True, max_length=255)
	icq = models.CharField(blank=True, max_length=30)
	jabber = models.CharField(blank=True, max_length=60)
	location = models.CharField(blank=True, max_length=60)
	website = models.URLField(blank=True, verify_exists=False)
	timezone = models.FloatField(choices=TIMEZONE_CHOICES, default=float(get_config('DEFAULT_TIME_ZONE', 0)))

	show_avatars = models.BooleanField(blank=True, default=True)
	show_smileys = models.BooleanField(blank=True, default=True)
	show_signatures = models.BooleanField(blank=True, default=True)

	def _get_post_count(self):
		return Post.objects.filter(author__exact=self).count()
	post_count = property(_get_post_count)

	class Meta:
		verbose_name_plural = ('Profiles')

	def __unicode__(self):
		return u"%s's profile" % self.user.username
	
	def get_absolute_url(self):
		return reverse('trinitee.accounts.views.profile_details', {'user_id': self.id})

class Avatar(models.Model):
	profile = models.OneToOneField(User)
	image = models.ImageField(upload_to="/uploads/avatars")

	class Meta:
		verbose_name_plural = ('Avatars')
	
	def get_absolute_url(self):
		return image.url

class ActivationKey(models.Model):
	user = models.OneToOneField(User)
	key = models.CharField(max_length=100)
	expires_at = models.DateTimeField()

	def save(self, *args, **kwargs):
		self.key = User.objects.make_random_password()
		self.expires_at = datetime.datetime.now() + \
			datetime.timedelta(days=get_config('ACTIVATION_KEY_EXPIRY_TIME', 7))
		super(ActivationKey, self).save(*args, **kwargs)

def post_save_signal_receiver(sender, **kwarg):
	if kwarg['created']:
		user = kwarg['instance']
		group, created = Group.objects.get_or_create(name='Users')
		if created:
			group.permissions.add(Permission.objects.get(codename='add_topic'))
			group.permissions.add(Permission.objects.get(codename='add_post'))
			group.save()
		user.groups.add(group)
		user.save()
		profile = UserProfile(user=user)
		profile.save()

post_save.connect(post_save_signal_receiver, sender=User,
	dispatch_uid="accounts.models")