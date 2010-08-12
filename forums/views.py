import math
from datetime import datetime, timedelta
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import F, Q, Count
from django.template import RequestContext
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from forums.forms import (PostForm, DeletePostForm, TopicForm,
	DeleteTopicForm, MoveTopicForm, ReportPostForm, SplitPostsForm,
	PostSearchForm)
from forums.models import Category, Forum, Topic, Post, PostKarma, Report
from utilities.annoying.decorators import render_to
from utilities.annoying.functions import get_config, get_object_or_None
from utilities.internal.decorators import user_passes_test_or_403
from utilities.internal.templatetags.forums import (can_access_forum,
	can_post_topic, can_post_reply)


@render_to('forums/index.html')
def index(request):
	users_online = cache.get('forums_users_online')
	if users_online == None:
		users_online = list(User.objects.filter(profile__last_activity_at__gte=
			(datetime.now()-timedelta(minutes=15))))
		cache.set('forums_users_online', users_online)

	categories = cache.get('forums_categories_%s' % request.user.id
		if request.user.is_authenticated() else 'anon')
	if categories == None:
		#forums = list(Forum.objects.all(). \
		#	select_related('category', 'last_post__topic', 'last_post__author'))
		forums = list(Forum.objects.annotate(num_can_read=Count('can_read')). \
			select_related('category', 'last_post__topic', 'last_post__author'))
		forums = [i for i in forums
			if can_access_forum(request, i, return_plain_boolean=True)]
		categories = {}
		for forum in forums:
			cat = categories.setdefault(forum.category.id,
				{'id': forum.category.id, 'category': forum.category, 'forums': []})
			cat['forums'].append(forum)
		cmpdef = lambda a, b: cmp(a['category'].order, b['category'].order)
		categories = sorted(categories.values(), cmpdef)
		cache.set('forums_categories_%s' % request.user.id
			if request.user.is_authenticated() else 'anon', categories)

	posts = cache.get('forums_count_posts')
	if posts == None:
		posts = Post.objects.count()
		cache.set('forums_count_posts', posts)

	topics = cache.get('forums_count_topics')
	if topics == None:
		topics = Topic.objects.count()
		cache.set('forums_count_topics', topics)

	users = cache.get('forums_count_users')
	if users == None:
		users = User.objects.count()
		cache.set('forums_count_users', users)

	return {'categories': categories, 'users_online': users_online,
			'posts': posts, 'topics': topics, 'users': users}


@render_to('forums/forum.html')
def forum_view(request, forum_id):
	forum = cache.get('forums_forum_%s' % forum_id)
	if forum == None:
		forum = get_object_or_404(Forum.objects \
			.annotate(num_can_read=Count('can_read')), pk=forum_id)
		cache.set('forums_forum_%s' % forum_id, forum)
	can_access = can_access_forum(request, forum)
	if not can_access == True:
		return can_access
	topics = cache.get('forums_topics_%s' % forum_id)
	if topics == None:
		topics = list(Topic.objects.filter(forum__pk=forum_id). \
			order_by('-is_sticky', '-created_at'). \
			select_related('author', 'last_post__author'))
		cache.set('forums_topics_%s' % forum_id, topics)
	return {'forum': forum, 'topics': topics}


@render_to('forums/topic.html')
def topic_view(request, topic_id):
	topic = cache.get('forums_topic_%s' % topic_id)
	if topic == None:
		topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
		cache.set('forums_topic_%s' % topic_id, topic)
	can_access = can_access_forum(request, topic.forum)
	if not can_access == True:
		return can_access
	if request.user.is_authenticated():
		topic.update_read(request.user)
	Topic.objects.filter(pk=topic_id).update(view_count=F('view_count') + 1) # FIXME ++ with cache
	posts = cache.get('forums_posts_%s' % topic_id)
	if posts == None:
		posts = list(Post.objects.filter(topic__pk=topic_id) \
			.select_related('author__profile__group', 'karma'))
		cache.set('forums_posts_%s' % topic_id, posts)
	return {'topic': topic, 'posts': posts, 'first_post_id': posts[0].id}


def post_permalink(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	older_posts = Post.objects.filter(topic__pk=post.topic.id,
		created_at__lt=post.created_at).count()
	page = int(math.ceil((float(older_posts) + 1.0) /
		get_config('POSTS_PER_PAGE', 25)))
	return redirect(post.topic.get_absolute_url() + '?page=%s#post-%s' % (page, post.id))


@login_required
@render_to('forums/topic_new.html')
def topic_new(request, forum_id):
	forum = get_object_or_404(Forum, pk=forum_id)
	if not can_post_topic(request.user, forum):
		messages.error(request, "You are not allowed to to post new topics \
			on this forum.")
		return redirect(forum.get_absolute_url())
	if request.method == 'POST':
		form = TopicForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			content = form.cleaned_data['content']
			topic = Topic(title=title, author=request.user, forum=forum)
			topic.save()
			post = Post(topic=topic, author=request.user,
				author_ip=request.META['REMOTE_ADDR'], content=content)
			post.save()
			messages.success(request, "Your topic has been saved.")
			return redirect(topic.get_absolute_url())
	else:
		form = TopicForm()
	return {'forum': forum, 'form': form}


@login_required
@render_to('forums/post_new.html')
def post_new(request, topic_id, quoted_post_id=None):
	topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
	if topic.is_closed:
		if not request.user.is_staff:
			messages.error(request, "You are not allowed to post in closed topics.")
			return redirect(topic.get_absolute_url())
		else:
			messages.info(request, "Note: This topic is closed.")
	if not can_post_reply(request.user, topic.forum):
		messages.error(request, "You are not allowed to reply on this forum.")
		return redirect(topic.get_absolute_url())
	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid():
			content = form.cleaned_data['content']
			post = Post(topic=topic, author=request.user,
				author_ip=request.META['REMOTE_ADDR'], content=content)
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
				messages.warning(request, "You tried to quote a post which "
					"doesn't exist or it doesn't belong to topic you are "
					"replying to. Nice try, Kevin.")
	return {'topic': topic, 'form': form}


@login_required
@render_to('forums/post_edit.html')
def post_edit(request, post_id):
	post = get_object_or_404(Post.objects.select_related(), pk=post_id)
	if not request.user.is_staff:
		if post.topic.is_closed:
			messages.error(request, "You are not allowed to edit posts \
				in closed topics.")
			return redirect(topic.get_absolute_url())
		if not post.author == request.user:
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


@login_required
@render_to('forums/post_delete.html')
def post_delete(request, post_id):
	post = get_object_or_404(Post.objects.select_related(), pk=post_id)
	if not request.user.is_staff:
		messages.error(request, "You are not allowed to delete this post.")
		return redirect(topic.get_absolute_url())
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


@login_required
@render_to('forums/topic_delete.html')
def topic_delete(request, topic_id):
	topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
	if not request.user.is_staff:
		messages.error(request, "You are not allowed to delete this topic.")
		return redirect(topic.get_absolute_url())
	if request.method == 'POST':
		if not 'cancel' in request.POST and 'confirmation' in request.POST:
			topic.delete()
			messages.success(request, "Topic has been deleted.")
			return redirect(topic.forum.get_absolute_url())
		return redirect(topic.get_absolute_url())
	else:
		form = DeleteTopicForm()
		messages.warning(request, "You are about to delete a topic "
			"with all posts belonging to it. Be ABSOLUTELY sure "
			"what you are doing, because this action cannot be reverted.")
	return {'topic': topic, 'form': form}


@login_required
@render_to('forums/report_form.html')
def post_report(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	if request.method == 'POST':
		form = ReportPostForm(request.POST)
		if form.is_valid():
			report = Report(post=post, reported_by=request.user,
				content=form.cleaned_data['content'])
			report.save()
			messages.success(request, "Your report has been saved. \
				One our staff members will review it shortly.")
			return redirect(post.get_absolute_url())
	else:
		form = ReportPostForm()
	return {'post': post, 'form': form}


@user_passes_test_or_403(lambda u: u.is_staff)
def topic_close(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	topic.is_closed = True
	topic.save()
	cache.set('forums_topic_%s' % topic_id, topic)
	messages.success(request, "Closed.")
	return redirect(topic.get_absolute_url())


@user_passes_test_or_403(lambda u: u.is_staff)
def topic_open(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	topic.is_closed = False
	topic.save()
	cache.set('forums_topic_%s' % topic_id, topic)
	messages.success(request, "Opened.")
	return redirect(topic.get_absolute_url())


@user_passes_test_or_403(lambda u: u.is_staff)
def topic_stick(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	topic.is_sticky = True
	topic.save()
	cache.set('forums_topic_%s' % topic_id, topic)
	messages.success(request, "Sticked.")
	return redirect(topic.get_absolute_url())


@user_passes_test_or_403(lambda u: u.is_staff)
def topic_unstick(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	topic.is_sticky = False
	topic.save()
	cache.set('forums_topic_%s' % topic_id, topic)
	messages.success(request, "Unsticked.")
	return redirect(topic.get_absolute_url())


@user_passes_test_or_403(lambda u: u.is_staff)
@render_to('forums/topic_move.html')
def topic_move(request, topic_id):
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


@user_passes_test_or_403(lambda u: u.is_staff)
@render_to('forums/posts_delete.html')
def posts_delete(request, topic_id):
	topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
	if request.method == 'POST':
		post_ids = request.POST.getlist('posts_selected')
	else:
		post_ids = request.GET.getlist('posts_selected')
	if not post_ids:
		messages.error(request, "You haven't checked any post.")
		return redirect(topic.get_absolute_url())
	if topic.first_post.id in post_ids:
		messages.error(request, "You cannot delete topic's first post."
			" Delete whole topic.")
		return redirect(topic.get_absolute_url())
	if request.method == 'POST':
		if not 'cancel' in request.POST and 'confirmation' in request.POST:
			posts = Post.objects.filter(pk__in=post_ids, topic=topic)
			topic.post_count = F('post_count') - len(posts)
			topic.forum.post_count = F('forum__post_count') - len(posts)
			posts.delete()
			topic.save()
			topic.forum.save()
			messages.success(request, "Post has been deleted.")
		return redirect(topic.get_absolute_url())
	else:
		form = DeletePostForm()
		messages.warning(request, "You are about to delete selected posts. \
			Be ABSOLUTELY sure what you are doing, because this action \
			cannot be reverted.")
		return {'topic': topic, 'form': form, 'posts_selected': post_ids}


@user_passes_test_or_403(lambda u: u.is_staff)
@render_to('forums/posts_split.html')
def posts_split(request, topic_id):
	topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
	if request.method == 'POST':
		post_ids = request.POST.getlist('posts_selected')
	else:
		post_ids = request.GET.getlist('posts_selected')
	if not post_ids:
		messages.error(request, "You haven't checked any post.")
		return redirect(topic.get_absolute_url())
	if topic.first_post.id in post_ids:
		messages.error(request, "You cannot split out topic's first post.")
		return redirect(topic.get_absolute_url())
	if request.method == 'POST':
		if not 'cancel' in request.POST and 'confirmation' in request.POST:
			posts = Post.objects.filter(pk__in=post_ids, topic=topic) \
				.order_by('id')
			topic.post_count = F('post_count') - len(posts)
			new_topic = Topic(author=posts[0].author,
				title=form.cleaned_data['new_title'], forum=topic.forum,
				post_count=len(posts), first_post=post[0])
			new_topic.save()
			posts.update(topic=new_topic)
			topic.save()
			messages.success(request, "Posts have been splitted.")
		return redirect(topic.get_absolute_url())
	else:
		form = SplitPostsForm()
		return {'topic': topic, 'form': form, 'posts_selected': post_ids}


@user_passes_test_or_403(lambda u: u.is_staff)
def topic_action(request, topic_id):
	topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
	try:
		action = request.GET['topic_action']
	except KeyError:
		return redirect(topic.get_absolute_url())
	# <del>I hate this.</del><ins>Could be worse.</ins>
	allowed_methods = ['topic_delete', 'topic_move', 'topic_open',
		'topic_close', 'topic_stick', 'topic_unstick', 'posts_delete',
		'posts_split']
	if action in allowed_methods:
		return globals().get(action)(request, topic_id)
	return redirect(topic.get_absolute_url())


@login_required
@render_to('forums/search_latest.html')
def search_latest(request):
	topics = cache.get('forums_topics_latest_%s' % request.user.id)
	if topics == None:
		topics = list(Topic.objects.filter(last_post__created_at__gte= \
			(datetime.now()-timedelta(days=1)).select_related()))
		cache.set('forums_topics_latest_%s' % request.user.id, topics)
	return {'topics': topics}


@login_required
@render_to('forums/search_unread.html')
def search_unread(request):
	topics = cache.get('forums_topics_unread_%s' % request.user.id)
	if topics == None:
		topics = list(Topic.objects.filter(last_post__created_at__gte= \
			request.user.post_tracking.last_read).select_related())
		cache.set('forums_topics_unread_%s' % request.user.id, topics)
	return {'topics': topics}


class PostSearchView(SearchView):

	def __init__(self, *args, **kwargs):
		super(PostSearchView, self).__init__(*args, **kwargs)
		self.template='forums/search.html'
		self.form_class=PostSearchForm
		self.searchqueryset=SearchQuerySet().models(Topic)

	def __name__(self):
		return "PostSearchView"

	def get_query(self):
		if self.form.is_valid():
			if self.form.cleaned_data['show_as'] == 'posts':
				self.template = 'forums/search_as_posts.html'
			return self.form.cleaned_data['q']
		return ''


def post_vote(request, post_id, value):
	post = get_object_or_None(Post, pk=post_id)
	if post == None:
		return ("You tried to vote for unexisting post.", True)
	if post.author == request.user:
		return ("You tried to vote for your own post.", False)
	karma, created = PostKarma.objects.get_or_create(post=post,
		user=request.user, defaults={'karma': value})
	""" refresh cache before incrementing karma counter """
	post.get_karma(force_refresh=True)
	if not created and not karma.karma == value:
		"""
			This actually works, so don't try to fix it.

			No really, don't.

			If you still don't believe me, the line below
			subtracts current karma value and adds new one.
		"""
		cache.incr('forums_karma_%s' % post_id, - karma.karma + value)
		karma.karma = value
		karma.save()
	return post


@login_required
def post_voteup(request, post_id):
	result = post_vote(request, post_id, 1)
	if not isinstance(result, Post):
		messages.error(request, result[0])
		if result[1]:
			return redirect(reverse('forums.views.index'))
	messages.info(request, "Saved.")
	return post_permalink(request, post_id)


@login_required
def post_votecancel(request, post_id):
	result = post_vote(request, post_id, 0)
	if not isinstance(result, Post):
		messages.error(request, result[0])
		if result[1]:
			return redirect(reverse('forums.views.index'))
	messages.info(request, "Saved.")
	return post_permalink(request, post_id)


@login_required
def post_votedown(request, post_id):
	result = post_vote(request, post_id, -1)
	if not isinstance(result, Post):
		messages.error(request, result[0])
		if result[1]:
			return redirect(reverse('forums.views.index'))
	messages.info(request, "Saved.")
	return post_permalink(request, post_id)
