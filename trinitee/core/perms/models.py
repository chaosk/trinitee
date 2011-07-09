from django.contrib.contenttypes.models import ContentType
from django.db import models


class PermissionedModel(models.Model):
	"""Model with permission helpers"""
	
	class Meta:
		abstract = True
	
	@models.permalink
	def get_permissions_url(self):
		return ('core.perms.views.perms_detail', (), {'contenttype_id':
			ContentType.objects.get_for_model(self.__class__).id,
			'object_id': self.id})

