from django import forms
from django.contrib.auth.models import User
from accounts.models import UserProfile
from forums.models import Forum
from utils.annoying.functions import get_config
from utils.django_recaptcha import ReCaptchaField

SORT_USER_BY_CHOICES = (
	('username', "Username"),
	('registered', "Registered"),
	('post_count', "No. of posts"),
)

SORT_POST_BY_CHOICES = (
	('posted_at', "Post time"),
	('author', "Author"),
	('title', "Subject"),
	('forum', "Forum"),
)

SORT_DIR_CHOICES = (
	('ASC', "Ascending"),
	('DESC', "Descending"),
)

SHOW_AS_CHOICES = (
	('topics', "Topics"),
	('posts', "Posts"),
)

SEARCH_IN_CHOICES = (
	('all', "Message text and topic subject"),
	('message', "Message text only"),
	('topic', "Topic subject only"),
)


class LoginForm(forms.Form):
	username = forms.CharField(min_length=2, max_length=30, label="Username")
	password = forms.CharField(min_length=4, label="Password",
		widget=forms.PasswordInput(render_value=False))


class RegistrationForm(forms.Form):
	username = forms.CharField(min_length=2, max_length=30, label="Username")
	password = forms.CharField(min_length=4, label="Password",
		widget=forms.PasswordInput(render_value=False))
	password_confirmation = forms.CharField(min_length=4,
		label="Confirm password", widget=forms.PasswordInput(render_value=False))
	email = forms.EmailField(label="E-mail address")
	email_confirmation = forms.EmailField(label="Confirm e-mail")
	if get_config('ENABLE_CAPTCHA', False):
		recaptcha = ReCaptchaField()

	def clean_username(self):
		username = self.cleaned_data.get('username')
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			return username
		self._errors['username'] = self.error_class(["This username is \
			already taken."])
		return username

	def clean(self):
		cleaned_data = self.cleaned_data
		email = cleaned_data.get('email')
		email_confirmation = cleaned_data.get('email_confirmation')
		password = cleaned_data.get('password')
		password_confirmation = cleaned_data.get('password_confirmation')

		# FIXME this should be rewritten.
		if email and email_confirmation and not email == email_confirmation:
			msg = "E-mail addresses do not match."
			self._errors['email'] = self.error_class([msg])
			self._errors['email_confirmation'] = self.error_class([msg])

			# These fields are no longer valid.
			del cleaned_data['email']
			del cleaned_data['email_confirmation']

		if password and password_confirmation and \
			not password == password_confirmation:
			msg = "Passwords do not match."
			self._errors['password'] = self.error_class([msg])
			self._errors['password_confirmation'] = self.error_class([msg])

			# These fields are no longer valid.
			del cleaned_data['password']
			del cleaned_data['password_confirmation']

		return cleaned_data


class ResendActivationKeyForm(forms.Form):
	email = forms.EmailField(label="E-mail address you've used to \
		register on this site")


class SettingsAvatarForm(forms.ModelForm):
	delete = forms.BooleanField(initial=False, label="Delete avatar?")

	class Meta:
		model = UserProfile
		fields = ['avatar']


class SettingsDisplayForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		fields = ['show_avatars', 'show_smileys', 'show_signatures', 'timezone']


class SettingsIdentityForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		fields = ['realname', 'location', 'icq', 'jabber', 'website']


class SettingsSignatureForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		fields = ['signature']


class UserSearchForm(forms.Form):
	username = forms.CharField(required=False, label="Username")
	sort_by = forms.ChoiceField(required=False, choices=SORT_USER_BY_CHOICES,
		label="Sort by")
	sort_dir = forms.ChoiceField(required=False, choices=SORT_DIR_CHOICES,
		label="Sort order")

	def filter(self, queryset):
		if self.is_valid():
			username = self.cleaned_data['username']
			sort_by = self.cleaned_data['sort_by']
			sort_dir = self.cleaned_data['sort_dir']
			if sort_by == 'username':
				if sort_dir == 'DESC':
					return queryset.filter(username__contains=username).order_by('-username')
				return queryset.filter(username__contains=username).order_by('username')
			elif sort_by == 'registered':
				if sort_dir == 'DESC':
					return queryset.filter(username__contains=username). \
						order_by('-date_joined')
				return queryset.filter(username__contains=username).order_by('date_joined')
			elif sort_by == 'post_count':
				if sort_dir == 'ASC':
					return queryset.filter(username__contains=username). \
						order_by('profile__post_count')
				return queryset.filter(username__contains=username). \
					order_by('-profile__post_count')
			else:
				if sort_dir == 'DESC':
					return queryset.all().order_by('-username')
		return queryset.all()


class PostSearchForm(forms.Form):
	keywords = forms.CharField(required=False, label="Keyword search",
		max_length=100)
	author = forms.CharField(required=False, label="Author search", max_length=25)
	#forum = forms.ModelChoiceField(choices=Forum.objects.all(), required=False, \
	# label="Forum")
	search_in = forms.ChoiceField(choices=SEARCH_IN_CHOICES, label="Search in")
	sort_by = forms.ChoiceField(choices=SORT_POST_BY_CHOICES, label="Sort by")
	sort_dir = forms.ChoiceField(choices=SORT_DIR_CHOICES, label="Sort order")
	show_as = forms.ChoiceField(choices=SHOW_AS_CHOICES, label="Show results as")

	def filter(self, queryset):
		# TODO add filtering
		return queryset
