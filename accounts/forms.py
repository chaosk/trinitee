from django import forms

class LoginForm(forms.Form):
	username = forms.CharField(min_length=2, max_length=30, label='Username')
	password = forms.CharField(min_length=4, label='Password', widget=forms.PasswordInput(render_value=False))		

class RegistrationForm(forms.Form):
	username = forms.CharField(min_length=2, max_length=30, label='Username')
	password = forms.CharField(min_length=4, label='Password', widget=forms.PasswordInput(render_value=False))
	password_confirmation = forms.CharField(min_length=4, label='Confirm password', widget=forms.PasswordInput(render_value=False))
	email = forms.EmailField(label='E-mail')
	email_confirmation = forms.EmailField(label='Confirm e-mail')
	# TODO recaptcha
	
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

		if password and password_confirmation and not password == password_confirmation:
			msg = "Passwords do not match."
			self._errors['password'] = self.error_class([msg])
			self._errors['password_confirmation'] = self.error_class([msg])

			# These fields are no longer valid.
			del cleaned_data['password']
			del cleaned_data['password_confirmation']

		return cleaned_data