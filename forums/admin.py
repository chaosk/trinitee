from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from forums.models import Category, Forum, Topic, Post, Report
from utilities.internal.templatetags.truncate import truncate


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


def mark_as_approved(modeladmin, request, queryset):
	queryset.update(status=True)
mark_as_approved.short_description = "Mark selected reports as approved"


def mark_as_ignored(modeladmin, request, queryset):
	queryset.update(status=False)
mark_as_ignored.short_description = "Mark selected reports as ignored"


class ReportAdmin(admin.ModelAdmin):
	list_display = ('id', 'change_list_status', 'status', 'urlized_post', \
		'reported_by', 'format_reported_at', 'truncated_content')
	list_display_links = ('id', 'change_list_status')
	list_filter = ('status',)
	fieldsets = (
		(None, {
			'fields': ('status', 'post', 'reported_by', 'reviewed_by', 'content')
		}),
	)
	readonly_fields = ('status', 'post', 'reported_by', 'reviewed_by', 'content')
	actions = [mark_as_approved, mark_as_ignored]

	def save_model(self, request, obj, form, change):
		if not change:
			return
		obj.reviewed_by = request.user
		if '_ignore' in request.POST:
			obj.status = False
			del request.POST['_ignore']
		elif '_approve' in request.POST:
			obj.status = True
			del request.POST['_approve']
		obj.save()

	def change_list_status(self, obj):
		return 'check'
	change_list_status.short_description = 'Check'

	def format_reported_at(self, obj):
		return obj.reported_at.strftime('%Y-%m-%d %H:%M')
	format_reported_at.short_description = 'Reported at'
	format_reported_at.admin_order_field = 'reported_at'

	def urlized_post(self, obj):
		return '<a href="%s">#%d, %s</a>' % (obj.post.get_absolute_url(), obj.post.id, obj.post.author)
	urlized_post.allow_tags = True
	urlized_post.short_description = 'Post'

	def truncated_content(self, obj):
		return truncate(obj.content, 70)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Report, ReportAdmin)
