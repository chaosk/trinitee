from django.db import models
from utils.internal.file_storage import OverwriteStorage

class Version(models.Model):
	version_number = models.CharField(max_length=10)
	release_notes = models.TextField(blank=True)

	def __unicode__(self):
		return self.version_number

class Platform(models.Model):
	name = models.CharField(max_length=10)
	displayed_name = models.CharField(max_length=20)

	def __unicode__(self):
		return self.displayed_name

class Release(models.Model):
	version = models.ForeignKey('Version', related_name='releases')
	platform = models.ForeignKey('Platform', related_name='releases')

	def release_filename(self, filename):
		fname, dot, extension = filename.rpartition('.')
		return 'uploads/releases/teeworlds-%s-%s.%s' % (self.version.version_number, self.platform.name, extension)

	uploaded_file = models.FileField(upload_to=release_filename,
		storage=OverwriteStorage())

	class Meta:
		unique_together = ('version', 'platform')

	def __unicode__(self):
		return u"%s-%s" % (self.version.version_number, self.platform.name)

	def get_absolute_url(self):
		return self.uploaded_file.url