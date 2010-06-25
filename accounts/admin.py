from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from accounts.models import Badge, UserProfile


class UserProfileInline(admin.StackedInline):
	model = UserProfile
	exclude = ('post_count',)


class UserProfileAdmin(UserAdmin):
	inlines = UserAdmin.inlines + [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
admin.site.register(Badge)
