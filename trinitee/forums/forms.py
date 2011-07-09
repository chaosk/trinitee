from django import forms
from forums.models import Post, Topic


class TopicNewForm(forms.ModelForm):

	class Meta:
		model = Topic
		fields = ('title', )


class PostNewForm(forms.ModelForm):

	class Meta:
		model = Post
		fields = ('content', )


class QModMoveForm(forms.ModelForm):

	class Meta:
		model = Topic
		fields = ('category', )

