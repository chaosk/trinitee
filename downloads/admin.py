from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from downloads.models import Platform, Release, Version


class PlatformAdmin(admin.ModelAdmin):
	pass


class ReleaseAdmin(admin.ModelAdmin):
	pass


class ReleaseInline(admin.TabularInline):
	model = Release


class VersionAdmin(admin.ModelAdmin):
	inlines = [ReleaseInline]


admin.site.register(Platform, PlatformAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Version, VersionAdmin)