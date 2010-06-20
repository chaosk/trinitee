from django.contrib import admin
from forums.models import Category, Forum, Topic


class ForumInline(admin.TabularInline):
	model = Forum
	exclude = ('description', 'last_post', 'post_count', 'topic_count')


class CategoryAdmin(admin.ModelAdmin):
	list_display = ('order_link', 'name')
	list_display_links = ('name', )
	inlines = [ForumInline]


class ForumAdmin(admin.ModelAdmin):
	list_display = ('order_link', 'name')
	list_display_links = ('name', )
	exclude = ('last_post', 'post_count', 'topic_count')


class TopicAdmin(admin.ModelAdmin):
	exclude = ('first_post', 'last_post', 'view_count', 'post_count')
		

admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
