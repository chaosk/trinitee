from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	avatar = models.ForeignKey('Avatar')
	signature = models.CharField(blank=True, max_length=255)
	location = models.TextField(blank=True)
	website = models.URLField(blank=True, verify_exists=False)
	post_count = models.IntegerField(blank=True, null=True)

	class Meta:
		ordering = ('')
		get_latest_by = ''
		verbose_name_plural = ('Profiles')

	def __unicode__(self):
		return u"Profile of %s" % self.user.username
	
	def get_absolute_url(self):
		return "/profile/%s" % self.id

class Avatar(models.Model):
	profile = models.OneToOneField(User)
	image = models.ImageField(upload_to="/uploads/avatars")

	class Meta:
		verbose_name_plural = ('Avatars')
	
	def get_absolute_url(self):
		return image.url

def post_save_signal_receiver(sender, **kwarg):
	if isinstance(kwarg['instance'], User) and kwarg['created'] == True:
		profile = UserProfile(user=kwarg['instance'])
		profile.save()

post_save.connect(post_save_signal_receiver)