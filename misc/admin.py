import datetime
from django import forms
from django.contrib import admin
from misc.models import Ban, WarningReason
from utilities.internal.templatetags.truncate import truncate


class BanAdminForm(forms.ModelForm):

	class Meta:
		model = Ban
		widgets = {
			'comment': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
		}


class BanAdmin(admin.ModelAdmin):
	list_display = ('id', 'created_at', 'banned_user', 'banned_mask',
		'expires_at', 'has_expired', 'truncated_comment')
	list_display_links = ('id', 'created_at')
	raw_id_fields = ('banned_user', )
	form = BanAdminForm

	def save_model(self, request, obj, form, change):
		if change:
			obj.modified_by = request.user
		else:
			obj.created_by = request.user
		obj.save()

	def add_view(self, request):
		self.exclude = ('created_by', 'modified_by')
		return super(BanAdmin, self).add_view(request)

	def change_view(self, request, obj_id):
		self.readonly_fields = ('created_by', 'modified_by')
		return super(BanAdmin, self).change_view(request, obj_id)

	def has_expired(self, obj):
		return True if datetime.datetime.now() > obj.expires_at else False
	has_expired.boolean = True

	def truncated_comment(self, obj):
		return truncate(obj.comment, 70)
	truncated_comment.short_description = 'Comment'


admin.site.register(Ban, BanAdmin)
admin.site.register(WarningReason)
