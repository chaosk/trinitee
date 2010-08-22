from haystack import indexes
from haystack import site
from forums.models import Post, Topic


class PostIndex(indexes.SearchIndex):
	text = indexes.CharField(document=True, use_template=True)
	topic_id = indexes.CharField(model_attr='topic__id')
	title = indexes.CharField(model_attr='topic__title')
	created_at = indexes.DateTimeField(model_attr='created_at')
	author = indexes.CharField(model_attr='author')


class TopicIndex(indexes.SearchIndex):
	text = indexes.CharField(document=True, use_template=True)
	title = indexes.CharField(model_attr='title')
	created_at = indexes.DateTimeField(model_attr='created_at')
	author = indexes.CharField(model_attr='author')


site.register(Post, PostIndex)
site.register(Topic, TopicIndex)
