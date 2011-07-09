from django.contrib import admin
from forums.models import Category
from guardian.admin import GuardedModelAdmin

class CategoryAdmin(GuardedModelAdmin):
	list_display = ('title', 'parent', 'ordering')
	list_display_links = ('title',)

admin.site.register(Category, CategoryAdmin)