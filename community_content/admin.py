from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from community_content.models import Map, Tileset


class ItemAdmin(admin.ModelAdmin):
	""" Just an "abstract" admin class """

	list_display = ('created_at', 'created_by', 'name', 'comment_count', 'rating')
	list_display_links = ('created_at', 'name')

	def save_model(self, request, obj, form, change):
		if change:
			obj.modified_by = request.user
		else:
			obj.created_by = request.user
		obj.save()

	def add_view(self, request):
		self.exclude = ('created_by', 'modified_by', 'comment_count', 'slug'
			'description_html')
		return super(ItemAdmin, self).add_view(request)

	def change_view(self, request, obj_id):
		self.readonly_fields = ('created_by', 'modified_by')
		self.exclude = ('comment_count', 'description_html')
		return super(ItemAdmin, self).change_view(request, obj_id)


class MapAdmin(ItemAdmin):
	list_display = ('created_at', 'created_by', 'gametype', 'tileset', 'name',
		'comment_count', 'rating')


class TilesetAdmin(ItemAdmin):
	pass


admin.site.register(Map, MapAdmin)
admin.site.register(Tileset, TilesetAdmin)