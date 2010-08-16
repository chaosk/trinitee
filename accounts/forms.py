from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.files.images import get_image_dimensions
from accounts.models import UserProfile
from forums.models import Forum
from utilities.annoying.functions import get_config
from utilities.django_recaptcha import ReCaptchaField


SORT_USER_BY_CHOICES = (
	('username', "Username"),
	('registered', "Registered"),
	('post_count', "No. of posts"),
)


SORT_DIR_CHOICES = (
	('ASC', "Ascending"),
	('DESC', "Descending"),
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
		if not get_config('RECAPTCHA_PUBLIC_KEY', False) \
			or not get_config('RECAPTCHA_PRIVATE_KEY', False):
			raise ImproperlyConfigured("You must define the RECAPTCHA_PUBLIC_KEY"
				" and/or RECAPTCHA_PRIVATE_KEY setting in order to use reCAPTCHA.")
		recaptcha = ReCaptchaField()

	def clean_username(self):
		username = self.cleaned_data.get('username')
		try:
			user = User.objects.get(username=username)
			raise forms.ValidationError("This username is already taken.")
		except User.DoesNotExist:
			return username

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if email and User.objects.filter(email=email).count():
			raise forms.ValidationError("Email addresses must be unique.")
		return email

	def clean(self):
		cleaned_data = self.cleaned_data
		email = cleaned_data.get('email')
		email_confirmation = cleaned_data.get('email_confirmation')
		password = cleaned_data.get('password')
		password_confirmation = cleaned_data.get('password_confirmation')

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
	delete = forms.BooleanField(required=False, initial=False,
		label="Delete avatar?")

	class Meta:
		model = UserProfile
		fields = ['avatar']

	def clean_avatar(self):
		avatar = self.cleaned_data.get('avatar')
		delete = self.cleaned_data.get('delete')
		if not avatar or delete:
			return avatar
		else:
			w, h = get_image_dimensions(avatar)
			max_w = get_config('AVATAR_MAX_WIDTH', 60)
			max_h = get_config('AVATAR_MAX_HEIGTH', 60)
			# TODO add max file size
			if w > max_w:
				raise forms.ValidationError("The image is %i pixel wide. "
					"It's supposed to be %ipx" % (w, max_h))
			if h > max_h:
				raise forms.ValidationError("The image is %i pixel high. "
					"It's supposed to be %ipx" % (h, max_h))
		return avatar


class SettingsDisplayForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		fields = ['show_avatars', 'show_smileys', 'show_signatures', 'timezone']


class SettingsIdentityStaffForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		fields = ['group', 'title', 'location', 'icq', 'jabber', 'website']


class SettingsIdentityForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		fields = ['location', 'icq', 'jabber', 'website']


class SettingsIdentityUserForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ['first_name', 'last_name']


class SettingsSignatureForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		fields = ['signature']
		widgets = {
			'signature': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
		}


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
			if username:
				queryset = queryset.filter(username__icontains=username)
			if sort_by == 'username':
				queryset = queryset.order_by('username')
			elif sort_by == 'registered':
				queryset = queryset.order_by('date_joined')
			elif sort_by == 'post_count':
				if sort_dir == 'ASC':
					queryset = queryset.order_by('profile__post_count')
				else:
					queryset = queryset.order_by('-profile__post_count')
				return queryset
			if sort_dir == 'DESC':
				queryset = queryset.reverse()
		return queryset
