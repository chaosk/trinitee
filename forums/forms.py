from django import forms

class PostForm(forms.Form):
	content = forms.CharField(label='Message', widget=forms.Textarea())

class TopicForm(forms.Form):
	title = forms.CharField(max_length=100, label='Topic subject')
	content = forms.CharField(label='Message', widget=forms.Textarea())