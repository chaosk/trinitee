from django import forms
from wiki.models import WikiPage
from lib.templatefilters import slugify


class WikiNewForm(forms.ModelForm):

	class Meta:
		model = WikiPage
		fields = ('title', 'content')

	def clean_title(self):
		if slugify(self.cleaned_data['title']) in ('new', 'list'):
			raise forms.ValidationError('This title is not allowed.')
		return self.cleaned_data['title']


class WikiEditForm(forms.ModelForm):
	comment = forms.CharField()

	class Meta:
		model = WikiPage
		fields = ('content', )
