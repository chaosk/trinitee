from django import forms
from forums.models import Forum, Topic
from haystack.forms import HighlightedSearchForm


SORT_POST_BY_CHOICES = (
	('posted_at', "Post time"),
	('author', "Author"),
	('title', "Subject"),
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


class DeleteTopicForm(DeletePostForm):
	pass


class TopicForm(forms.Form):
	title = forms.CharField(max_length=60, label="Topic subject")
	content = forms.CharField(label="Message", widget=forms.Textarea())


class MoveTopicForm(forms.Form):
	forum = forms.ModelChoiceField(queryset=Forum.objects.all())


class ReportPostForm(forms.Form):
	content = forms.CharField(label="Reason", max_length=255,
		widget=forms.Textarea())


class SplitPostsForm(forms.Form):
	title = forms.CharField(max_length=60, label="New topic subject")


class PostSearchForm(HighlightedSearchForm):
	q = forms.CharField(label="Search", min_length=4)
	sort_by = forms.ChoiceField(required=False, choices=SORT_POST_BY_CHOICES,
		label="Sort by")
	sort_dir = forms.ChoiceField(required=False, choices=SORT_DIR_CHOICES,
		label="Sort order")
	show_as = forms.ChoiceField(required=False, choices=SHOW_AS_CHOICES,
		label="Show results as")

	def search(self):
		sqs = super(PostSearchForm, self).search()
		if self.cleaned_data['sort_by'] == 'author':
			if self.cleaned_data['sort_dir'] == 'DESC':
				sqs = sqs.order_by('-author')
			sqs = sqs.order_by('author')
		elif self.cleaned_data['sort_by'] == 'posted_at':
			if self.cleaned_data['sort_dir'] == 'DESC':
				sqs = sqs.order_by('-created_at')
			sqs = sqs.order_by('created_at')
		elif self.cleaned_data['sort_by'] == 'title':
			if self.cleaned_data['sort_dir'] == 'DESC':
				sqs = sqs.order_by('-title')
			sqs = sqs.order_by('title')
		else:
			if self.cleaned_data['sort_dir'] == 'DESC':
				sqs = sqs.order_by('-created_at')
		return sqs
