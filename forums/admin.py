from django.contrib import admin
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet
from forums.models import Category, Forum, Topic, Post, Report
from utilities.internal.templatetags.truncate import truncate
from utilities.internal.widgets import NullBooleanROWidget, PostPreviewWidget


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
	list_display = ('category', 'order_link', 'name')
	list_display_links = ('name',)
	exclude = ('last_post', 'post_count', 'topic_count')


class PostInline(admin.TabularInline):
	model = Post
	max_num = 1
	extra = 1
	exclude = ('content_html',)
	formset = RequiredInlineFormSet


class TopicAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'first_post_author', 'created_at',
		'post_count', 'is_closed', 'is_sticky')
	list_display_links = ('id', 'title')
	exclude = ('first_post', 'last_post', 'view_count', 'post_count')
	inlines = [PostInline]

	def close_topic(modeladmin, request, queryset):
		queryset.update(is_closed=True)
	close_topic.short_description = "Close selected topics"

	def open_topic(modeladmin, request, queryset):
		queryset.update(is_closed=False)
	open_topic.short_description = "Open selected topics"

	def stick_topic(modeladmin, request, queryset):
		queryset.update(is_sticky=True)
	stick_topic.short_description = "Stick selected topics"

	def unstick_topic(modeladmin, request, queryset):
		queryset.update(is_sticky=False)
	unstick_topic.short_description = "Unstick selected topics"

	actions = [close_topic, open_topic, stick_topic, unstick_topic]

	def first_post_author(self, obj):
		return '<a href="%s">%s</a>' % \
			(obj.first_post.author.get_absolute_url(), obj.first_post.author)
	first_post_author.allow_tags = True
	first_post_author.short_description = 'Topic starter'


class ReportAdminForm(ModelForm):
	class Meta:
		model = Report
		widgets = {
			'status': NullBooleanROWidget(),
			'post': PostPreviewWidget(),
		}


class ReportAdmin(admin.ModelAdmin):
	list_display = ('id', 'change_list_status', 'status', 'urlized_post', \
		'reported_by', 'format_reported_at', 'truncated_content')
	list_display_links = ('id', 'change_list_status')
	list_filter = ('status',)
	form = ReportAdminForm
	fieldsets = (
		(None, {
			'fields': ('status', 'post', 'reported_by', 'reviewed_by', 'content')
		}),
	)
	readonly_fields = ('reported_by', 'reviewed_by', 'content')

	def mark_as_approved(modeladmin, request, queryset):
		queryset.update(status=True)
	mark_as_approved.short_description = "Mark selected reports as approved"

	def mark_as_ignored(modeladmin, request, queryset):
		queryset.update(status=False)
	mark_as_ignored.short_description = "Mark selected reports as ignored"

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
	truncated_content.short_description = 'Report content'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Report, ReportAdmin)
