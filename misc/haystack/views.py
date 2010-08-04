from haystack.views import SearchView

class PostSearchView(SearchView):
	def __name__(self):
		return "PostSearchView"

	def get_query(self):
		if self.form.is_valid():
			if self.form.cleaned_data['show_as'] == 'posts':
				self.template = 'misc/search/post_view_forum_search.html'
			return self.form.cleaned_data['q']
		return ''