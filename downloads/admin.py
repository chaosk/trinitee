from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from downloads.models import Platform, Release, Version
from utilities.internal.templatetags.truncate import truncate


class PlatformAdmin(admin.ModelAdmin):
	pass


class ReleaseInline(admin.TabularInline):
	model = Release


class VersionAdmin(admin.ModelAdmin):
	list_display = ['version_number', 'is_published', 'format_created_at', 'truncated_release_notes']
	inlines = [ReleaseInline]
	
	def format_created_at(self, obj):
		return obj.created_at.strftime('%Y-%m-%d %H:%M')
	format_created_at.short_description = 'Created at'
	format_created_at.admin_order_field = 'created_at'
	
	def truncated_release_notes(self, obj):
		return truncate(obj.release_notes, 100)
	truncated_release_notes.short_description = 'Release notes'


admin.site.register(Platform, PlatformAdmin)
admin.site.register(Version, VersionAdmin)
