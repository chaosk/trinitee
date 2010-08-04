from django import forms
from django.contrib import admin
from django.contrib.auth.models import User, Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from accounts.models import Badge, UserProfile, Group, Warn
from utilities.internal.templatetags.truncate import truncate


class UserProfileInlineAdminForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		widgets = {
			'about': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
			'signature': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
		}


class UserProfileInline(admin.StackedInline):
	model = UserProfile
	form = UserProfileInlineAdminForm
	fieldsets = (
		("Credentials, badges", {
			'fields': ('group', 'badges', 'title'),
		}),
		("Avatar, signature", {
			'fields': ('avatar', 'signature', 'about'),
		}),
		("Identity", {
			'fields': ('location', 'icq', 'jabber', 'website'),
		}),
	)


class UserAdmin(DjangoUserAdmin):
	list_display = ('id', 'username', 'is_active', 'email', 'realname',
		'group', 'is_staff', 'is_superuser')
	list_display_links = ('id', 'username')
	inlines = DjangoUserAdmin.inlines + [UserProfileInline]
	fieldsets = (
		(None, {
			'fields': ('username', 'password'),
		}),
		("Personal info", {
			'fields': ('first_name', 'last_name', 'email'),
		}),
		("Permissions", {
			'fields': ('is_active', 'is_staff', 'is_superuser'),
		}),
		("Important dates", {
			'fields': ('last_login', 'date_joined'),
		}),
	)

	def realname(self, obj):
		return "%s %s" % (obj.first_name, obj.last_name)
	realname.admin_order_field = 'last_name'

	def group(self, obj):
		return obj.profile.group


class GroupAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'user_title', 'is_staff_group')
	list_display_links = ('id', 'name')


class BadgeAdmin(admin.ModelAdmin):
	list_display = ('id', 'preview_badge', 'title', 'description')
	list_display_links = ('id', 'title')

	def save_model(self, request, obj, form, change):
		if 'badge' in request.FILES:
			obj.badge.save('%s.png' % request.user.id, request.FILES['badge'])
		obj.save()

	def preview_badge(self, obj):
		return '<img src="%s" />' % obj.badge.url
	preview_badge.allow_tags = True
	preview_badge.short_description = "Badge"


class WarnAdminForm(forms.ModelForm):

	class Meta:
		model = Warn
		widgets = {
			'comment': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
		}


class WarnAdmin(admin.ModelAdmin):
	list_display = ('id', 'created_at', 'weight', 'reason',
		'user', 'truncated_comment')
	list_display_links = ('id', 'created_at')
	raw_id_fields = ('user', )
	form = WarnAdminForm

	def save_model(self, request, obj, form, change):
		if change:
			obj.modified_by = request.user
		else:
			obj.created_by = request.user
		obj.save()

	def add_view(self, request):
		self.exclude = ('created_by', 'modified_by')
		return super(WarnAdmin, self).add_view(request)

	def change_view(self, request, obj_id):
		self.readonly_fields = ('created_by', 'modified_by')
		return super(WarnAdmin, self).change_view(request, obj_id)

	def truncated_comment(self, obj):
		return truncate(obj.comment, 70)
	truncated_comment.short_description = "Comment"

# I'm terribly sorry, I had to do that, because I HATE DJANGO
admin.site.unregister([User, DjangoGroup])
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(Warn, WarnAdmin)
