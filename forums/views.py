from django.shortcuts import render_to_response, redirect, \
	get_object_or_404, get_list_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from forums.forms import PostForm, TopicForm
from forums.models import Category, Forum, Topic, Post

def index(request):
	categories = Category.objects.all()
	for c in categories:
		c.forums = list(Forum.objects.filter(category=c))
	return render_to_response('forums/index.html', {'categories': categories},
		context_instance=RequestContext(request))

def forum_view(request, forum_id, page=1):
	forum = get_object_or_404(Forum, pk=forum_id)
	topics = list(Topic.objects.filter(forum__pk=forum_id))
	return render_to_response('forums/forum.html', {'forum': forum,
		'topics': topics}, context_instance=RequestContext(request))

def topic_view(request, topic_id, page=1, post_id=False):
	topic = get_object_or_404(Topic, pk=topic_id)
	posts = list(Post.objects.filter(topic__pk=topic_id))
	return render_to_response('forums/topic.html', {'topic': topic,
		'posts': posts}, context_instance=RequestContext(request))

@login_required
def topic_new(request, forum_id):
	forum = get_object_or_404(Forum, pk=forum_id)
	if request.method == 'POST':
		form = TopicForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			content = form.cleaned_data['content']
			
			topic = Topic(title=title, forum=forum)
			topic.save()
			post = Post(topic=topic, author=request.user, content=content)
			post.save()
			messages.success(request, "Your topic has been saved.")
			return redirect(topic.get_absolute_url())
	else:
		form = TopicForm()
	return render_to_response('forums/topic_new.html', {'forum': forum,
		'form': form}, context_instance=RequestContext(request))

def post_view(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	return render_to_response('forums/post.html', {'post': post},
		context_instance=RequestContext(request))

@login_required
def post_new(request, topic_id, quoted_post_id=None):
	topic = get_object_or_404(Topic, pk=topic_id)
	if topic.is_closed and not request.user.is_staff:
		messages.error(request, "You are not allowed to post in closed topics.")
		return redirect(topic.get_absolute_url())
	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid():
			content = form.cleaned_data['content']
			
			post = Post(topic=topic, author=request.user, content=content)
			post.save()
			messages.success(request, "Your reply has been saved.")
			return redirect(post.get_absolute_url())
	else:
		form = TopicForm()
		if quoted_post_id:
			try:
				quoted_post = Post.objects.get(pk=quoted_post_id, topic=topic)
				form.initial = {'content': "[quote=%s]%s[/quote]" % (quoted_post.author, quoted_post.content)}
			except Post.DoesNotExist:
				messages.warning(request, "You tried to quote a post which doesn't exist or \
					it doesn't belong to topic you are replying to.")
	return render_to_response('forums/post_new.html', {'topic': topic,
		'form': form}, context_instance=RequestContext(request))