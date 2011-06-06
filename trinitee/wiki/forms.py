from django import forms
from wiki.models import WikiPage


class WikiNewForm(forms.ModelForm):

	class Meta:
		model = WikiPage
		fields = ('title', 'content')


class WikiEditForm(forms.ModelForm):
	comment = forms.CharField()

	class Meta:
		model = WikiPage
		fields = ('content', )
