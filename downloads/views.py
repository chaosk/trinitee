from django.core.cache import cache
from downloads.models import Version
from utilities.annoying.functions import get_config, get_object_or_None
from utilities.annoying.decorators import render_to
from utilities.httpagentparser import os_detect

@render_to('downloads/downloads.html')
def downloads(request):
	versions = cache.get('downloads_versions')
	if versions == None:
		versions = list(Version.objects.reverse()[:5])
		cache.set('downloads_versions', versions, 86400)
	return {'versions': versions}