import datetime
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from forums.models import Post
from utils.annoying.functions import get_config

class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True)
	avatar = models.ForeignKey('Avatar', blank=True, null=True)
	signature = models.CharField(blank=True, max_length=255)
	location = models.TextField(blank=True)
	website = models.URLField(blank=True, verify_exists=False)

	def _get_post_count(self):
		return Post.objects.filter(author__exact=self).count()
	post_count = property(_get_post_count)

	class Meta:
		verbose_name_plural = ('Profiles')

	def __unicode__(self):
		return u"%s's profile" % self.user.username
	
	def get_absolute_url(self):
		return "/profile/%s" % self.id

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