from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from forums.forms import TopicForm
from forums.models import Category, Forum, Topic, Post

def index(request):
	categories = Category.objects.all()
	for c in categories:
		c.forums = list(Forum.objects.filter(category=c))
	return render_to_response('forums/index.html', {'categories': categories}, context_instance=RequestContext(request))

def forum_view(request, forum_id, page=1):
	forum = get_object_or_404(Forum, pk=forum_id)
	topics = list(Post.objects.filter(topic__forum__pk=forum_id))
	return render_to_response('forums/forum.html', {'forum': forum, 'topics': topics}, context_instance=RequestContext(request))

def topic_view(request, topic_id, page=1, post_id=False):
	posts = get_list_or_404(Post, topic__pk=topic_id)
	return render_to_response('forums/topic.html', {'posts': posts}, context_instance=RequestContext(request))

def topic_new(request, forum_id):
	forum = get_object_or_404(Forum, pk=forum_id)
	if request.method == 'POST':
		form = TopicForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			content = form.cleaned_data['content']
			# FDSFDJS
			
	else:
		form = TopicForm()
	return render_to_response('forums/topic_new.html', {'form': form}, context_instance=RequestContext(request))

def post_view(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	return render_to_response('forums/post.html', {'post': post}, context_instance=RequestContext(request))