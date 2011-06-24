from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from annoying.decorators import render_to
from forums.models import Category, Topic, Post


@render_to('forums/index.html')
def forum_index(request):
	categories = Category.objects.filter(parent__isnull=False) \
		.select_related()
	return {
		'categories': categories,
	}


@render_to('forums/topic_list.html')
def topic_list(request, category_id):
	category = get_object_or_404(Category, pk=category_id)
	topics = Topic.objects.filter(category=category)
	return {
		'category': category,
		'topics': topics,
	}


@render_to('forums/topic_detail.html')
def topic_detail(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	posts = Post.objects.filter(topic=topic)
	return {
		'topic': topic,
		'posts': posts,
	}


@render_to('forums/topic_new.html')
def topic_new(request, category_id):
	# TODO check credentials
	category = get_object_or_404(Category, pk=category_id)
	topic_form = TopicNewForm()
	post_form = PostNewForm()
	if request.method == 'POST':
		topic_form = TopicNewForm(request.POST)
		post_form = PostNewForm(request.POST)
		if topic_form.is_valid() and post_form.is_valid():
			# add post preview
			new_topic = topic_form.save()
			new_post = post_form.save()
			messages.success(request, "Successfully created a new topic.")
			return redirect(new_topic.get_absolute_url())
	return {
		'category': category,
		'topic_form': topic_form,
		'post_form': post_form,
	}


@render_to('forums/post_new.html')
def post_new(request, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	if topic_id.is_closed:
		if request.user.is_staff:
			messages.info(request, "This topic is closed.")
		else:
			messages.error(request,
				"You are not allowed to post in closed topics."
			)
			return redirect(topic.get_absolute_url())

	form = PostNewForm()
	if request.method == 'POST':
		form = PostNewForm(request.POST)
		if form.is_valid():
			# add post preview
			form.save()
			messages.success(request,
				"Your reply has been saved."
			)
			return redirect(post.get_absolute_url())
	return {
		'topic': topic,
		'form': form,
	}

@render_to('forums/post_edit.html')
def post_edit(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	topic = post.topic
	if request.user.is_staff:
		if topic.is_closed:
			messages.error(request,
				"You are not allowed to edit posts in closed topics."
			)
			return redirect(topic.get_absolute_url())
		if not post.created_by == request.user:
			messages.error(request, "You are not allowed to edit this post.")
			return redirect(topic.get_absolute_url())
		
	form = PostEditForm(instance=post)
	if request.method == 'POST':
		form = PostEditForm(request.POST, instance=post)
		if form.is_valid():
			form.save()
			messages.success(request,
				"{0} has been updated." \
				.format("Your post" if request.user == post.created_by else "Post")
			)
			return redirect(post.get_absolute_url())
	return {
		'page': page,
		'form': form,
	}


@render_to('forums/post_delete.html')
def post_delete(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	if not request.user.is_staff and not post.id == post.topic.last_post.id:
		# add a timedelta condition
		messages.error(request, "You are not allowed to delete this post.")
		return redirect(topic.get_absolute_url())
	if request.method == 'POST':
		if post.id == post.topic.first_post_id:
			post.topic.delete()
			messages.success(request,
				"Successfully removed this topic."
			)
			return redirect(post.topic.forum.get_absolute_url())
		else:
			post.delete()
			messages.success(request,
				"Successfully removed {0} post." \
				.format("your" if request.user == post.created_by else "this")
			)
			return redirect(post.topic.get_absolute_url())
	else:
		if post.id == post.topic.first_post_id:
			messages.warning(request,
				"This action will delete whole topic with all posts within."
			)
	return {
		'post': post,
	}
