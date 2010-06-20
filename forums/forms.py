from django import forms
from forums.models import Forum

SORT_POST_BY_CHOICES = (
	('posted_at', "Post time"),
	('author', "Author"),
	('title', "Subject"),
	('forum', "Forum"),
)

SORT_DIR_CHOICES = (
	('ASC', "Ascending"),
	('DESC', "Descending"),
)

SHOW_AS_CHOICES = (
	('topics', "Topics"),
	('posts', "Posts"),
)

SEARCH_IN_CHOICES = (
	('all', "Message text and topic subject"),
	('message', "Message text only"),
	('topic', "Topic subject only"),
)


class PostForm(forms.Form):
	content = forms.CharField(label="Message", widget=forms.Textarea())


class DeletePostForm(forms.Form):
	confirmation = forms.BooleanField(label="Delete confirmation", required=False)


class TopicForm(forms.Form):
	title = forms.CharField(max_length=100, label="Topic subject")
	content = forms.CharField(label="Message", widget=forms.Textarea())


class MoveTopicForm(forms.Form):
	forum = forms.ModelChoiceField(queryset=Forum.objects.all())


class PostSearchForm(forms.Form):
	keywords = forms.CharField(label="Keyword search",
		min_length=3, max_length=100)
	author = forms.CharField(required=False, label="Author search", max_length=25)
	#forum = forms.ModelChoiceField(choices=Forum.objects.all(), required=False, \
	# label="Forum")
	search_in = forms.ChoiceField(choices=SEARCH_IN_CHOICES, label="Search in")
	sort_by = forms.ChoiceField(choices=SORT_POST_BY_CHOICES, label="Sort by")
	sort_dir = forms.ChoiceField(choices=SORT_DIR_CHOICES, label="Sort order")
	show_as = forms.ChoiceField(choices=SHOW_AS_CHOICES, label="Show results as")

	def filter(self, queryset):
		# TODO add filtering
		return queryset
