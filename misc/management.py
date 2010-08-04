from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_syncdb


def prompt_for_site(sender, **kwargs):
	if not hasattr(settings, "SITE_DOMAIN") or not settings.SITE_DOMAIN:
		raise ImproperlyConfigured("You must define the SITE_DOMAIN setting "
		"before using the syncdb command.")
	site, created = Site.objects.get_or_create(pk=1)
	site.domain = settings.SITE_DOMAIN
	site.save()

post_syncdb.connect(prompt_for_site)
