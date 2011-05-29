from django.db import models
from django.template.defaultfilters import slugify
from markdown import markdown


class WikiPage(models.Model):
	""" A wiki page """

	title = models.CharField(max_length=50)
	slug = models.SlugField()
	content = models.TextField()
	content_html = models.TextField()
	updated = models.DateTimeField(auto_now_add=True)

	def slugify_title(self):
		new_slug = slug = slugify(self.title) or "bad-title"
		# preventing slugs from being non-unique, wordpress-style
		n = 1
		while True:
			try:
				WikiPage.objects.get(slug=new_slug)
			except WikiPage.DoesNotExist:
				break
			n += 1
			if n != 1:
				new_slug = "{0}-{1}".format(slug, n)
		return new_slug

	def save(self, *args, **kwargs):
		self.slug = self.slugify_title()
		self.content_html = markdown(self.content)
		super(WikiPage, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.title
