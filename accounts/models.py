import datetime
from pytz import common_timezones
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.utils.hashcompat import sha_constructor
from forums.models import Post
from utilities import postmarkup
from utilities.annoying.functions import get_config
from utilities.internal.file_storage import OverwriteStorage

TIMEZONE_CHOICES = tuple([(tz, tz) for tz in common_timezones])


class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True, related_name='profile')
	last_activity_at = models.DateTimeField(auto_now_add=True)
	last_activity_ip = models.IPAddressField(blank=True, null=True)
	badge = models.ForeignKey('Badge', default=1, blank=True, null=True)
	title = models.CharField(blank=True, max_length=30)
	avatar = models.ImageField(blank=True, default='',
		storage=OverwriteStorage(), upload_to='uploads/avatars/')
	signature = models.CharField(blank=True, max_length=255)
	signature_html = models.CharField(blank=True, max_length=500)
	icq = models.CharField(blank=True, max_length=30)
	jabber = models.CharField(blank=True, max_length=60)
	location = models.CharField(blank=True, max_length=60)
	website = models.URLField(blank=True, verify_exists=False)
	timezone = models.CharField(choices=TIMEZONE_CHOICES, default='UTC',
		max_length=25)

	show_avatars = models.BooleanField(blank=True, default=True)
	show_smileys = models.BooleanField(blank=True, default=True)
	show_signatures = models.BooleanField(blank=True, default=True)

	post_count = models.PositiveIntegerField(default=0)

	class Meta:
		verbose_name_plural = ('Profiles')

	def __unicode__(self):
		return u"%s's profile" % self.user.username

	def save(self, *args, **kwargs):
		if get_config('ENABLE_BBCODE', False):
			markup = postmarkup.create(annotate_links=False,
				use_pygments=get_config('BBCODE_USE_PYGMENTS', False))
			self.signature_html = markup(self.signature)
		else:
			self.signature_html = self.signature
		super(UserProfile, self).save(*args, **kwargs)

	@models.permalink
	def get_absolute_url(self):
		return ('accounts.views.profile_details', (), {'user_id': self.id})

	def get_post_count(self):
		return Post.objects.filter(author__exact=self).count()


class Badge(models.Model):
	title = models.CharField(max_length=20)
	is_for_superuser = models.BooleanField(default=False)
	is_for_staff = models.BooleanField(default=False)

	def badge_filename(self, filename):
		fname, dot, extension = filename.rpartition('.')
		return 'uploads/badges/%s.%s' % (self.title, extension)

	badge = models.ImageField(blank=True, default='',
		storage=OverwriteStorage(), upload_to=badge_filename)

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return self.badge.url

class ActivationKey(models.Model):
	user = models.OneToOneField(User)
	key = models.CharField(max_length=100)
	expires_at = models.DateTimeField()

	def save(self, *args, **kwargs):
		self.key = User.objects.make_random_password()
		self.expires_at = datetime.datetime.now() + \
			datetime.timedelta(days=get_config('ACTIVATION_KEY_EXPIRY_TIME', 7))
		super(ActivationKey, self).save(*args, **kwargs)


def post_save_user(sender, **kwargs):
	user = kwargs['instance']
	if kwargs['created']:
		if user.id == 0:
			# really special case
			return
		profile = UserProfile(user=user)
		profile.save()
	profile = user.profile
	if not user.is_superuser and not user.is_staff and profile.badge.id in \
		list(Badge.objects.filter(Q(is_for_staff=True) | Q(is_for_superuser=True))):
		# whenever user loses credentials, he should go back to default badge
		profile.badge = Badge.objects.get(pk= \
			UserProfile._meta.get_field('badge').default)
	elif not user.is_superuser and user.is_staff and profile.badge.id in \
		list(Badge.objects.filter(is_for_superuser=True)):
		profile.badge = Badge.objects.get(title="Moderator")
	profile.save()

post_save.connect(post_save_user, sender=User,
	dispatch_uid="accounts.models")
