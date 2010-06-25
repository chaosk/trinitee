from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from forums.models import Category, Forum, Topic, Post


class RequiredInlineFormSet(BaseInlineFormSet):

	def _construct_form(self, i, **kwargs):
		"""
		Override the method to change the form attribute empty_permitted
		"""
		form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
		form.empty_permitted = False
		return form


class ForumInline(admin.TabularInline):
	model = Forum
	exclude = ('description', 'last_post', 'post_count', 'topic_count')


class CategoryAdmin(admin.ModelAdmin):
	list_display = ('order_link', 'name')
	list_display_links = ('name',)
	inlines = [ForumInline]


class ForumAdmin(admin.ModelAdmin):
	list_display = ('order_link', 'name')
	list_display_links = ('name',)
	exclude = ('last_post', 'post_count', 'topic_count')


class PostInline(admin.TabularInline):
	model = Post
	max_num = 1
	extra = 1
	exclude = ('content_html',)
	formset = RequiredInlineFormSet

class TopicAdmin(admin.ModelAdmin):
	exclude = ('first_post', 'last_post', 'view_count', 'post_count')
	inlines = [PostInline]
		

admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
