from django import forms

class TopicForm(forms.Form):
	title = forms.CharField(max_length=100, label='Topic subject')
	content = forms.TextField(label='Message')