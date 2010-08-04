from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from forums.models import Category, Forum, Topic, Post, Report
from utilities.internal.templatetags.truncate import truncate
from utilities.internal.widgets import NullBooleanROWidget, PostPreviewWidget


class RequiredInlineFormSet(BaseInlineFormSet):
# We don't use it anymore, it can be used later though.

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
	list_display_links = ('name', )
	inlines = [ForumInline]


class ForumAdmin(admin.ModelAdmin):
	list_display = ('category', 'order_link', 'name')
	list_display_links = ('name', )
	exclude = ('last_post', 'post_count', 'topic_count')


class TopicAdminForm(forms.ModelForm):
	content = forms.CharField(widget=forms.Textarea())

	def __init__(self, *args, **kwargs):
		super(TopicAdminForm, self).__init__(*args, **kwargs)
		if kwargs.has_key('instance'):
			instance = kwargs['instance']
			content = instance.first_post.content
			self.fields['content'].initial = content

	class Meta:
		model = Topic


class TopicAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'urlized_author', 'created_at',
		'post_count', 'is_closed', 'is_sticky')
	list_display_links = ('id', 'title')
	form = TopicAdminForm
	fieldsets = [
		(None, {
			"fields": ('title', 'forum', 'is_sticky', 'is_closed', 'content')
		})
	]

	def save_model(self, request, obj, form, change):
		if change:
			obj.modified_by = request.user
			obj.first_post.modified_by = request.user
			obj.first_post.content = form.cleaned_data['content']
			obj.first_post.save()
			obj.save()
		else:
			obj.author = request.user
			obj.author_ip = request.META['REMOTE_ADDR']
			obj.save()
			post = Post(topic=obj, author=request.user,
				author_ip=request.META['REMOTE_ADDR'],
				content=form.cleaned_data['content'])
			post.save()

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

	def urlized_author(self, obj):
		return '<a href="%s">%s</a>' % \
			(obj.author.get_absolute_url(), obj.author)
	urlized_author.allow_tags = True
	urlized_author.short_description = 'Topic starter'


class ReportAdminForm(forms.ModelForm):

	class Meta:
		model = Report
		widgets = {
			'status': NullBooleanROWidget(),
			'post': PostPreviewWidget(),
		}


class ReportAdmin(admin.ModelAdmin):
	list_display = ('id', 'change_list_status', 'status', 'urlized_post', \
		'reported_by', 'reported_at', 'truncated_content')
	list_display_links = ('id', 'change_list_status')
	list_filter = ('status', )
	form = ReportAdminForm
	fieldsets = (
		(None, {
			'fields': ('status', 'post', 'reported_by', 'reviewed_by',
				'content'),
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

	def urlized_post(self, obj):
		return '<a href="%s">#%d, %s</a>' % (obj.post.get_absolute_url(),
			obj.post.id, obj.post.author)
	urlized_post.allow_tags = True
	urlized_post.short_description = 'Post'

	def truncated_content(self, obj):
		return truncate(obj.content, 70)
	truncated_content.short_description = 'Report content'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Report, ReportAdmin)
