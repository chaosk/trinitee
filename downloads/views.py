from downloads.models import Version
from utils.annoying.functions import get_config, get_object_or_None
from utils.annoying.decorators import render_to
from utils.httpagentparser import os_detect

@render_to('downloads/downloads.html')
def downloads(request):
	versions = Version.objects.reverse()[:5]
	return {'versions': versions}