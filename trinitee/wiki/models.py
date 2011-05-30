from django.contrib.auth.models import User
from django.db import models
from lib.templatefilters import slugify
from markdown import markdown


class WikiPage(models.Model):
	""" A wiki page """

	title = models.CharField(max_length=255, unique=True)
	slug = models.SlugField(unique=True)
	content = models.TextField()
	content_html = models.TextField()

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		self.content_html = markdown(self.content)
		super(WikiPage, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.title