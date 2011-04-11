import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
	def get_available_name(self, name):
		"""
		Returns a filename that's free on the target storage system, and
		available for new content to be written to.
		"""
		# If the filename already exists, remove it as if it was a true file system
		if self.exists(name):
			self.delete(name)
		return name


def generic_filename(self, filename):
	if self.hasattr('slug'):
		return "uploads/%s/%s-%s.%s" % (self._meta.verbose_name_plural,
			self.created_by.id, self.slug, filename.rpartition('.')[2])
	return "uploads/%s/%s.%s" % (self._meta.verbose_name_plural,
		self.created_by.id, filename.rpartition('.')[2])

