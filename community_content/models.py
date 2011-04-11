from django.core.cache import cache
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from utilities.djangoratings.fields import RatingField
from utilities.internal.file_storage import OverwriteStorage, generic_filename


class Item(models.Model):
	""" (Very) generic model. """
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User)
	modified_at = models.DateTimeField(auto_now=True)
	name = models.CharField(max_length=100)
	slug = models.SlugField(max_length=100)
	description = models.TextField(max_length=800)
	description_html = models.TextField(max_length=2000)
	rating = RatingField(range=5)
	comment_count = models.IntegerField(default=0)
	is_commenting_allowed = models.BooleanField(default=True)
	content_file = models.FileField(storage=OverwriteStorage(),
		upload_to=generic_filename)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		if get_config('ENABLE_BBCODE', False):
			markup = postmarkup.create(annotate_links=False,
				use_pygments=get_config('BBCODE_USE_PYGMENTS', False))
			self.description_html = markup(self.description)
		else:
			self.description_html = self.description
		super(Item, self).save(*args, **kwargs)

	class Meta:
		abstract = True
		unique_together = ('created_by', 'slug')


class Map(Item):
	gametype = models.CharField(max_length=20)
	tileset = models.CharField(max_length=20)


class Tileset(Item):
	pass


class ItemComment(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User)
	modified_at = models.DateTimeField(auto_now=True)
	content = models.CharField(max_length=500)
	content_html = models.TextField()

	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()


class Screenshot(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)

	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	
	screenshot_file = models.FileField(storage=OverwriteStorage(),
		upload_to=generic_filename)


def post_item_save(instance, **kwargs):
	if kwargs['created']:
		try:
			cache.incr('community_content_item_count')
		except ValueError:
			pass



post_save.connect(post_item_save)