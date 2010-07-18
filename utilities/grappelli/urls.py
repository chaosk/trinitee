# coding: utf-8

# DJANGO IMPORTS
from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('',
    
    # GENERIC
    url(r'^lookup/obj/$', 'utilities.grappelli.views.generic.generic_lookup', name="grp_generic_lookup"),
    # FOREIGNKEY LOOKUP
    url(r'^lookup/related/$', 'utilities.grappelli.views.related.related_lookup', name="grp_related_lookup"),
    url(r'^lookup/m2m/$', 'utilities.grappelli.views.related.m2m_lookup', name="grp_m2m_lookup"),
    
)
