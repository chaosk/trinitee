import datetime
import math
from django.shortcuts import redirect, get_object_or_404, get_list_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import F
from django.template import RequestContext
from forums.forms import PostForm, DeletePostForm, TopicForm, MoveTopicForm
from forums.models import Category, Forum, Topic, Post
from utils.annoying.decorators import render_to
from utils.annoying.functions import get_config
from utils.internal.decorators import has_perm_or_403, user_passes_test_or_403
from utils.internal.templatetags.forums import editable_by


@render_to('forums/index.html')
def index(request):
	forums = list(Forum.objects.all(). \
		select_related('category', 'last_post__topic', 'last_post__author'))
	categories = {}
	for forum in forums:
		cat = categories.setdefault(forum.category.id,
			{'id': forum.category.id, 'category': forum.category, 'forums': []})
		cat['forums'].append(forum)

	cmpdef = lambda a, b: cmp(a['category'].ordering, b['category'].ordering)
	categories = sorted(categories.values(), cmpdef)
	return {'categories': categories}


@render_to('forums/forum.html')
def forum_view(request, forum_id):
	forum = get_object_or_404(Forum, pk=forum_id)
	topics = list(Topic.objects.filter(forum__pk=forum_id). \
		select_related('author', 'last_post__author'))
	return {'forum': forum, 'topics': topics}


@render_to('forums/topic.html')
def topic_view(request, topic_id):
	topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
	if request.user.is_authenticated():
		topic.update_read(request.user)
	Topic.objects.filter(pk=topic_id).update(view_count=F('view_count') + 1)
	posts = list(Post.objects.filter(topic__pk=topic_id).select_related())
	return {'topic': topic, 'posts': posts, 'first_post_id': topic.first_post.id}


def post_permalink(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	older_posts = Post.objects.filter(topic__pk=post.topic.id,
		created_at__lt=post.created_at).count()
	page = int(math.ceil((float(older_posts) + 1.0) /
		get_config('POSTS_PER_PAGE', 25)))
	return redirect(reverse('forums.views.topic_view',
		kwargs={'topic_id': post.topic.id}) + '?page=%s#post-%s' % (page, post.id))


@has_perm_or_403('forums.add_topic')
@render_to('forums/topic_new.html')
def topic_new(request, forum_id):
	forum = get_object_or_404(Forum, pk=forum_id)
	if request.method == 'POST':
		form = TopicForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			content = form.cleaned_data['content']
			topic = Topic(title=title, author=request.user, forum=forum)
			topic.save()
			post = Post(topic=topic, author=request.user, content=content)
			post.save()
			messages.success(request, "Your topic has been saved.")
			return redirect(topic.get_absolute_url())
	else:
		form = TopicForm()
	return {'forum': forum, 'form': form}


@has_perm_or_403('forums.add_post')
@render_to('forums/post_new.html')
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
				form.initial = {'content': "[quote=%s]%s[/quote]" %
					(quoted_post.author, quoted_post.content)}
			except Post.DoesNotExist:
				messages.warning(request, "You tried to quote a post which doesn't \
					exist or it doesn't belong to topic you are replying to.")
	return {'topic': topic, 'form': form}


@login_required
@render_to('forums/post_edit.html')
def post_edit(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	if post.topic.is_closed and not request.user.is_staff:
		messages.error(request, "You are not allowed to edit posts \
			in closed topics.")
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
	return {'post': post, 'form': form}


@has_perm_or_403('forums.delete_post')
@render_to('forums/post_delete.html')
def post_delete(request, post_id):
	post = get_object_or_404(Post.objects.select_related(), pk=post_id)
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
		if post.id == post.topic.first_post.id:
			messages.warning(request, "This action will delete whole topic \
				with all posts within.")
		messages.warning(request, "You are about to delete a post. \
			Be ABSOLUTELY sure what you are doing, because this action \
			cannot be reverted.")
	return {'post': post, 'form': form}


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
@render_to('forums/topic_move.html')
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
	return {'topic': topic, 'form': form}
