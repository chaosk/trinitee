from django.shortcuts import render_to_response, redirect, \
	get_object_or_404, get_list_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from forums.forms import PostForm, DeletePostForm, TopicForm, MoveTopicForm
from forums.models import Category, Forum, Topic, Post
from utils.decorators import has_perm_or_403, user_passes_test_or_403
from utils.templatetags.forums import editable_by

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
	topic.view_count = topic.view_count + 1
	topic.save()
	if request.user.is_authenticated():
		topic.update_read(request.user)
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
		form = PostForm()
		if quoted_post_id:
			try:
				quoted_post = Post.objects.get(pk=quoted_post_id, topic=topic)
				form.initial = {'content': "[quote=%s]%s[/quote]" % (quoted_post.author, quoted_post.content)}
			except Post.DoesNotExist:
				messages.warning(request, "You tried to quote a post which doesn't exist or \
					it doesn't belong to topic you are replying to.")
	return render_to_response('forums/post_new.html', {'topic': topic,
		'form': form}, context_instance=RequestContext(request))

@login_required
def post_edit(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	if post.topic.is_closed and not request.user.is_staff:
		messages.error(request, "You are not allowed to edit posts in closed topics.")
		return redirect(topic.get_absolute_url())
	if not editable_by(post, request.user):
		messages.error(request, "You are not allowed to edit this post.")
		return redirect(topic.get_absolute_url())
	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid():
			content = form.cleaned_data['content']
			post.content = content
			post.modified_by = request.user
			post.save()
			messages.success(request, "Post has been saved.")
			return redirect(post.get_absolute_url())
	else:
		form = PostForm()
		form.initial = {'content': post.content}
	return render_to_response('forums/post_edit.html', {'post': post,
		'form': form}, context_instance=RequestContext(request))

@has_perm_or_403('forums.delete_post')
def post_delete(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	if request.method == 'POST':
		if not 'cancel' in request.POST and 'confirmation' in request.POST:
			post.delete()
			messages.success(request, "Post has been deleted.")
			try:
				Topic.objects.get(pk=post.topic.id)
			except Topic.DoesNotExist:
				return redirect(post.topic.forum.get_absolute_url())
		return redirect(post.topic.get_absolute_url())
	else:
		form = DeletePostForm()
		if post == post.topic.first_post:
			messages.warning(request, "This action with delete whole topic with all posts within.")
		messages.warning(request, "You are about to delete a post. \
			Be ABSOLUTELY sure what you are doing, because this action \
			cannot be reverted.")
	return render_to_response('forums/post_delete.html', {'post': post,
		'form': form}, context_instance=RequestContext(request))

@user_passes_test_or_403(lambda u: u.is_staff)
def close_topic(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	if topic.is_closed:
		message.info(request, "Topic is already closed!")
	else:
		topic.is_closed = True
		topic.save()
		messages.success(request, "Closed.")
	return redirect(topic.get_absolute_url())

@user_passes_test_or_403(lambda u: u.is_staff)
def open_topic(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	if not topic.is_closed:
		message.info(request, "Topic is already open!")
	else:
		topic.is_closed = False
		topic.save()
		messages.success(request, "Opened.")
	return redirect(topic.get_absolute_url())

@user_passes_test_or_403(lambda u: u.is_staff)
def stick_topic(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	if topic.is_sticky:
		message.info(request, "Topic is already sticked!")
	else:
		topic.is_sticky = True
		topic.save()
		messages.success(request, "Sticked.")
	return redirect(topic.get_absolute_url())

@user_passes_test_or_403(lambda u: u.is_staff)
def unstick_topic(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	if not topic.is_sticky:
		message.info(request, "Topic is already unsticked!")
	else:
		topic.is_sticky = False
		topic.save()
		messages.success(request, "Unsticked.")
	return redirect(topic.get_absolute_url())

@user_passes_test_or_403(lambda u: u.is_staff)
def move_topic(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	if request.method == 'POST':
		form = MoveTopicForm(request.POST)
		if form.is_valid():
			try:
				forum = Forum.objects.get(pk=form.cleaned_data['forum'].id)
			except Forum.DoesNotExist:
				messages.error(request, "You tried to move topic to unexisting forum.")
				return redirect(topic.get_absolute_url())
			topic.forum = forum
			topic.save()
		return redirect(topic.get_absolute_url())
	else:
		form = MoveTopicForm()
	return render_to_response('forums/topic_move.html', {'topic': topic,
		'form': form}, context_instance=RequestContext(request))