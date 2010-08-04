from django import forms
from forums.models import Topic
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


class PostSearchForm(HighlightedSearchForm):
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
