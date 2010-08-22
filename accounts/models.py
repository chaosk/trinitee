import datetime
from pytz import common_timezones
from django.contrib.auth.models import User, Permission
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from accounts.validators import validate_signature
from misc.models import Ban, StoredNotification, WarningReason
import forums
from utilities import postmarkup
from utilities.annoying.functions import get_config
from utilities.internal.file_storage import OverwriteStorage

TIMEZONE_CHOICES = tuple([(tz, tz) for tz in common_timezones])


class GroupManager(models.Manager):

	def get_by_natural_key(self, name):
		return self.get(name=name)


class Group(models.Model):
# I'm terribly sorry, I had to do that, because I HATE DJANGO
	objects = GroupManager()
	name = models.CharField(max_length=80, unique=True)
	user_title = models.CharField(max_length=20)
	is_staff_group = models.BooleanField(default=False,
		help_text="Setting this to True will automatically "
			"give group members is_staff status.")

	def group_badge_filename(self, filename):
		fname, dot, extension = filename.rpartition('.')
		return 'uploads/badges/group/%s.%s' % (self.id, extension)

	group_badge = models.ImageField(blank=True, default='',
		storage=OverwriteStorage(), upload_to=group_badge_filename)

	def __unicode__(self):
		return self.name


class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True, related_name='profile')
	last_activity_at = models.DateTimeField(auto_now_add=True)
	last_activity_ip = models.IPAddressField(blank=True, null=True)
	badges = models.ManyToManyField('Badge', blank=True, related_name='users')
	group = models.ForeignKey('Group', blank=True, null=True,
		help_text="User will get all permissions granted to group he/she is in.")
	admin_notes = models.CharField(blank=True, max_length=255)
	title = models.CharField(blank=True, max_length=30)

	def avatar_filename(self, filename):
		fname, dot, extension = filename.rpartition('.')
		return 'uploads/avatars/%s.%s' % (self.id, extension)
	avatar = models.ImageField(blank=True, default='',
		storage=OverwriteStorage(), upload_to=avatar_filename,
		help_text="Only gif, jpg and png files are allowed."
			" The maximum image size allowed is %sx%s pixels and %s." % \
			(get_config('AVATAR_MAX_WIDTH', 60), get_config('AVATAR_MAX_HEIGHT', 60),
			get_config('AVATAR_MAX_SIZE', 10240)))

	about = models.CharField(blank=True, max_length=800)
	about_html = models.CharField(blank=True, max_length=1500)
	signature = models.CharField(validators=[validate_signature],
		blank=True, max_length=300, help_text="Maximum size 300 characters long"
			" and %s lines high." % get_config('SIGNATURE_MAX_LINES', 4))
	signature_html = models.CharField(blank=True, max_length=600)
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
		if not self.user.is_superuser:
			is_staff_group = self.group.is_staff_group if self.group else False
			self.user.is_staff = is_staff_group
		if get_config('ENABLE_BBCODE', False):
			markup = postmarkup.create(annotate_links=False,
				use_pygments=get_config('BBCODE_USE_PYGMENTS', False))
			self.signature_html = markup(self.signature)
			self.about_html = markup(self.about)
		else:
			self.signature_html = self.signature
			self.about_html = markup(self.about)
		super(UserProfile, self).save(*args, **kwargs)

	@models.permalink
	def get_absolute_url(self):
		return ('accounts.views.profile_details', (), {'user_id': self.id})

	def get_post_count(self):
		return forums.models.Post.objects.filter(author__exact=self).count()


class Badge(models.Model):
	title = models.CharField(max_length=30)
	description = models.CharField(max_length=255)

	def badge_filename(self, filename):
		fname, dot, extension = filename.rpartition('.')
		return 'uploads/badges/user/%s.%s' % (self.id, extension)
	badge = models.ImageField(storage=OverwriteStorage(),
		upload_to=badge_filename)

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return self.badge.url


class ActivationKey(models.Model):
	user = models.OneToOneField(User)
	key = models.CharField(max_length=100)
	expires_at = models.DateTimeField()

	def save(self, *args, **kwargs):
		self.key = User.objects.make_random_password() # OK, not really a password
		self.expires_at = datetime.datetime.now() + \
			datetime.timedelta(days=get_config('ACTIVATION_KEY_EXPIRY_TIME', 7))
		super(ActivationKey, self).save(*args, **kwargs)


class Warn(models.Model):
# Python hatery: Warning and UserWarning are built-in exceptions.
	WEIGHTS = (
		(1, 1),
		(2, 2),
		(3, 3),
		(4, 4),
		(5, 5),
	)
	created_at = models.DateTimeField(auto_now_add=True)
	weight = models.IntegerField(choices=WEIGHTS, default=1)
	reason = models.ForeignKey(WarningReason)
	user = models.ForeignKey(User, related_name='warnings')
	created_by = models.ForeignKey(User, related_name='warns_given')
	modified_by = models.ForeignKey(User, related_name='warns_modified')
	comment = models.CharField(blank=True, max_length=1000)

	def __unicode__(self):
		return "%s (W:%s)" % (self.user.username, self.weight)


def post_user_save(instance, **kwargs):
	if kwargs['created']:
		if instance.id == 0: # really special case
			return
		profile = UserProfile(user=instance)
		profile.save()


def post_profile_save(instance, **kwargs):
	if not instance.group:
		# we like being fail-safe
		default_group, created = Group.objects.get_or_create(pk=1,
			defaults={'name': "Members", 'user_title': "Member"})
		instance.group = default_group
		instance.save()


def post_group_save(instance, **kwargs):
	""" Updates users is_staff status """
	members = User.objects.filter(is_superuser=False, profile__group=instance) \
		.update(is_staff=instance.is_staff_group)


def post_warning_save(instance, **kwargs):
	warn_count = sum(Warn.objects.filter(user=instance.user) \
		.values_list('weight', flat=True))
	firstban_count = get_config('WARNINGS_TO_FIRSTBAN', 4)
	permban_count = get_config('WARNINGS_TO_PERMBAN', 5)
	if warn_count >= permban_count:
		ban = Ban(created_by=instance.created_by, banned_user=instance.user,
			expires_at=False, comment="AUTO PERMANENT ban, sorry."
				"Here's last warning comment:\n%s" % instance.comment)
		ban.save()
	elif warn_count >= firstban_count:
		ban = Ban(created_by=instance.created_by, banned_user=instance.user,
			expires_at=datetime.datetime.now()+datetime.timedelta(days=7),
			comment="AUTO ban, sorry."
				"Here's last warning comment:\n%s" % instance.comment)
		ban.save()
	else:
		StoredNotification(user=instance.user,
			message="You have been warned (weight: %s) by %s.<br />Reason: %s"
				"<br />Additional comment:<br />%s<br /><br />"
				"You have %s warnings. You are on the way to destruction, "
				"make your time." % (instance.weight, instance.warned_by,
				instance.reason, instance.comment, warn_count), level=40)


post_save.connect(post_user_save, sender=User,
	dispatch_uid="accounts.models")
post_save.connect(post_profile_save, sender=UserProfile,
	dispatch_uid="accounts.models")
post_save.connect(post_group_save, sender=Group,
	dispatch_uid="accounts.models")
post_save.connect(post_warning_save, sender=Warn,
	dispatch_uid="accounts.models")
