import math
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template.response import TemplateResponse
from annoying.functions import get_config
from guardian.shortcuts import get_objects_for_user
from guardian.utils import get_anonymous_user
from markdown import markdown
from forums.forms import PostNewForm, TopicNewForm
from forums.models import Category, Topic, Post


def forums_index(request):
	if request.user.is_authenticated():
		user = request.user
	else:
		user = get_anonymous_user()
	categories = get_objects_for_user(user, 'forums.view_category')
	categories = categories.filter(parent__isnull=True).select_related()
	# FIXME currently all subcategories will be shown
	#       if an user has access to root category
	return TemplateResponse(request, 'forums/index.html', {
		'categories': categories,
	})


def topic_list(request, category_id):
	category = get_object_or_404(Category, pk=category_id)
	if not request.user.has_perm('forums.view_category', category):
		raise Http404
	topics = Topic.objects.filter(category=category).select_related()
	return TemplateResponse(request, 'forums/topic_list.html', {
		'category': category,
		'topics': topics,
	})


def topic_detail(request, category_id, topic_id):
	topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
	if not request.user.has_perm('forums.view_category', topic.category):
		raise Http404
	posts = Post.objects.filter(topic=topic).select_related()
	return TemplateResponse(request, 'forums/topic_detail.html', {
		'topic': topic,
		'posts': posts,
	})


@login_required
def topic_new(request, category_id):
	category = get_object_or_404(Category, pk=category_id)
	if not request.user.has_perm('forums.add_topics_category', category):
		messages.error(request,
			"You are not allowed to post new topics in this category."
		)
		return redirect(category.get_absolute_url())
	topic_form = TopicNewForm()
	post_form = PostNewForm()
	extra_context = {
		'category': category,
	}
	if request.method == 'POST':
		topic_form = TopicNewForm(request.POST)
		post_form = PostNewForm(request.POST)
		if topic_form.is_valid() and post_form.is_valid():
			if request.POST.get('preview'):
				extra_context['post_preview'] = markdown(post_form \
					.cleaned_data.get('content'))
			else:
				new_topic = topic_form.save(commit=False)
				new_topic.created_by = request.user
				new_topic.category = category
				new_topic.save()
				new_post = post_form.save(commit=False)
				new_post.created_by = request.user
				new_post.topic = new_topic
				new_post.save()
				messages.success(request, "Successfully created a new topic.")
				return redirect(new_topic.get_absolute_url())
	extra_context['topic_form'] = topic_form
	extra_context['post_form'] = post_form
	return TemplateResponse(request, 'forums/topic_new.html', extra_context)


@login_required
def post_new(request, category_id, topic_id):
	topic = get_object_or_404(Topic, pk=topic_id)
	if not request.user.has_perm('forums.add_posts_category', topic.category):
		messages.error(request,
			"You are not allowed to post new replies in this category."
		)
		return redirect(topic.get_absolute_url())
	if topic.is_closed:
		if request.user.has_perm('forums.add_posts_category', topic.category):
			messages.info(request, "This topic is closed.")
		else:
			messages.error(request,
				"You are not allowed to post in closed topics."
			)
			return redirect(topic.get_absolute_url())

	form = PostNewForm()
	extra_context = {
		'topic': topic,
	}
	if request.method == 'POST':
		form = PostNewForm(request.POST)
		if form.is_valid():
			if request.POST.get('preview'):
				extra_context['post_preview'] = markdown(form \
					.cleaned_data.get('content'))
			else:
				new_post = form.save(commit=False)
				new_post.created_by = request.user
				new_post.topic = topic
				new_post.save()
				messages.success(request,
					"Your reply has been saved."
				)
				return redirect(new_post.get_absolute_url())
	extra_context['form'] = form
	return TemplateResponse(request, 'forums/post_new.html', extra_context)


@login_required
def post_edit(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	topic = post.topic
	if not request.user.has_perm('forums.moderate_category', topic.category):
		if topic.is_closed:
			messages.error(request,
				"You are not allowed to edit posts in closed topics."
			)
			return redirect(topic.get_absolute_url())
		if not post.created_by == request.user or not post.id == topic.last_post.id:
			# add a timedelta condition
			messages.error(request, "You are not allowed to edit this post.")
			return redirect(topic.get_absolute_url())

	form = PostNewForm(instance=post)
	extra_context = {
		'post': post,
	}
	if request.method == 'POST':
		form = PostNewForm(request.POST, instance=post)
		if form.is_valid():
			if request.POST.get('preview'):
				extra_context['post_preview'] = markdown(form \
					.cleaned_data.get('content'))
			else:
				form.save()
				messages.success(request,
					"{0} has been updated.".format("Your post" \
						if request.user == post.created_by else "Post")
				)
				return redirect(post.get_absolute_url())
	extra_context['form'] = form
	return TemplateResponse(request, 'forums/post_edit.html', extra_context)


@login_required
def post_delete(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	if not request.user.has_perm('forums.moderate_category', post.topic.category):
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
	return TemplateResponse(request, 'forums/post_delete.html', {
		'post': post,
	})


def post_permalink(request, post_id):
	post = get_object_or_404(Post, pk=post_id)
	if not request.user.has_perm('forums.view_category', post.topic.category):
		raise Http404
	older_posts = Post.objects.filter(topic__pk=post.topic_id,
		created_at__lt=post.created_at).count()
	page = int(math.ceil((float(older_posts) + 1.0) /
		get_config('POSTS_PER_PAGE', 25)))
	return redirect("{0}{1}#post-{2}".format(
		post.topic.get_absolute_url(),
		"?page={0}".format(page) if page > 1 else '', post.id)
	)
