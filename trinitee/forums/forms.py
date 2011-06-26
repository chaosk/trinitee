from django import forms
from forums.models import Post, Topic


class TopicNewForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.category = kwargs.pop('category', None)
		if self.category is None:
			raise AttributeError("category missing")
		super(TopicNewForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Topic
		fields = ('title', )


class PostNewForm(forms.ModelForm):

	class Meta:
		model = Post
		fields = ('content', )
