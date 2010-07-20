from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from utilities import postmarkup
from utilities.annoying.functions import get_config


class Drawboard(models.Model):
	last_modified_at = models.DateTimeField(auto_now=True)
	last_modified_by = models.ForeignKey(User, blank=True, null=True)
	content = models.TextField(blank=True)
	content_html = models.TextField(blank=True)

	def save(self, *args, **kwargs):
		cache.delete('misc_drawboard')
		if get_config('ENABLE_BBCODE', False):
			markup = postmarkup.create(annotate_links=False,
				use_pygments=get_config('BBCODE_USE_PYGMENTS', False))
			self.content_html = markup(self.content)
		else:
			self.content_html = self.content
		super(Drawboard, self).save(*args, **kwargs)
		cache.set('misc_drawboard', self)
