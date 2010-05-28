from django import forms

class UserForm(forms.Form):
	username = forms.CharField(min_length=2, max_length=30, label='Username')
	email = forms.EmailField(label='E-mail')
	email_confirmation = forms.EmailField(label='Confirm e-mail')