from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
	username = forms.RegexField(label="Username", regex=r'^\w+$', min_length=2,
		max_length=30)
	password1 = forms.CharField(label="Password", min_length=4,
		widget=forms.PasswordInput(render_value=False),
		help_text="At least 4 chars long")
	password2 = forms.CharField(label="Password (again)", min_length=4,
		widget=forms.PasswordInput(render_value=False))
	email1 = forms.EmailField(label="E-mail address",
		help_text="We won't share this to any 3rd-parties!")
	email2 = forms.EmailField(label="E-mail address (again)")

	def clean_username(self):
		username = self.cleaned_data.get('username')
		try:
			user = User.objects.get(username__iexact=username)
			del user
			raise forms.ValidationError("Username is already taken")
		except User.DoesNotExist:
			pass
		return username

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 != password2:
			raise forms.ValidationError(
				"You must type the same password each time")
		return password2

	def clean_email2(self):
		email1 = self.cleaned_data.get('email1')
		email2 = self.cleaned_data.get('email2')
		if email1 != email2:
			raise forms.ValidationError(
				"You must type the same e-mail address each time")
		return email2

	def save(self):
		return User.objects.create_user(self.cleaned_data.get('username'),
			self.cleaned_data.get('email1'), self.cleaned_data.get('password1'))


class LoginForm(forms.Form):
	username = forms.CharField(label="Username")
	password = forms.CharField(label="Password",
		widget=forms.PasswordInput(render_value=False))

	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
		self.user = None

	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')

		if not username or not password:
			return self.cleaned_data
		self.user = authenticate(username=username, password=password)
		if self.user == None:
			raise forms.ValidationError("Invalid username and/or password")
		if not self.user.is_active:
			raise forms.ValidationError("Your account has been disabled")
		return self.cleaned_data
