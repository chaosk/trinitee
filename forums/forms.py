from django import forms
from forums.models import Forum


class PostForm(forms.Form):
	content = forms.CharField(label="Message", widget=forms.Textarea())


class DeletePostForm(forms.Form):
	confirmation = forms.BooleanField(label="Delete confirmation", required=False)


class DeleteTopicForm(DeletePostForm):
	pass

class TopicForm(forms.Form):
	title = forms.CharField(max_length=100, label="Topic subject")
	content = forms.CharField(label="Message", widget=forms.Textarea())


class MoveTopicForm(forms.Form):
	forum = forms.ModelChoiceField(queryset=Forum.objects.all())


class ReportPostForm(forms.Form):
	content = forms.CharField(label="Reason", max_length=255,
		widget=forms.Textarea())
