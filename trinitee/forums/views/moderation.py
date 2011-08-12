from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template.response import TemplateResponse
from forums.forms import QModMoveForm, TopicNewForm
from forums.models import Post, Topic


@login_required
# note:
#   Those actions are POST only, and confirmation is not required.
#   For some less serious actions (e.g. topic closing) it is wanted behaviour
#     and a redirect should be returned.
#   For irreversible (half-truth) actions, use another form to confirm.
def topic_quick_moderation(request, topic_id, **kwargs):
	topic = get_object_or_404(Topic, pk=topic_id)
	if not request.user.has_perm('forums.moderate_category', topic.category):
		raise Http404
	if request.method == 'POST':
		action = request.cleaned_data.get('action')
		# BTW: magic happens here
		allowed_methods = ['topic_delete', 'topic_move', 'topic_open',
				'topic_close', 'topic_stick', 'topic_unstick',
				'topic_delete_posts', 'topic_split']
		if action in allowed_methods:
			ret = globals().get('qmod_' + action)(request, topic)
			if ret != None:
				# confirmation-requiring methods (e.g. topic delete)
				return TemplateResponse(request,
					'forums/qmod_confirmation.html', ret)
	return redirect(topic.get_absolute_url())


def qmod_topic_delete(request, topic):
	if not 'confirmation' in request.POST:
		messages.warning(request,
			"Are you sure you want to delete this topic?")
		return {}
	topic.delete()
	messages.success(request, "Successfully removed topic.")
	return redirect(topic.category.get_absolute_url())


def qmod_topic_move(request, topic):
	if not 'confirmation' in request.POST:
		messages.info(request,
			"Specify category to which the topic should be moved.")
		return {
			'form': QModMoveForm(),
		}
	form = QModMoveForm(request.POST)
	if form.is_valid():
		form.save()
	messages.success(request, "Successfully moved topic.")


def qmod_topic_open(request, topic):
	topic.update(is_closed=False)
	messages.success(request, "Opened.")


def qmod_topic_close(request, topic):
	topic.update(is_closed=True)
	messages.success(request, "Closed.")


def qmod_topic_stick(request, topic):
	topic.update(is_sticky=True)
	messages.success(request, "Stickied.")


def qmod_topic_unstick(request, topic):
	topic.update(is_sticky=False)
	messages.success(request, "Unstickied.")


def qmod_topic_delete_posts(request, topic):
	# TODO add checkboxes to posts
	post_ids = request.POST.getlist('posts_selected')
	if not post_ids:
		messages.error(request, "You haven't selected any post.")
		return
	if not 'confirmation' in request.POST:
		messages.warning(request,
			"Are you sure you want to delete selected posts?")
		return {}
	posts = Post.objects.filter(topic=topic, pk__in=post_ids)
	if topic.first_post_id in post_ids:
		posts.exclude(pk=topic.first_post_id)
	posts.delete()
	messages.success(request, "Selected posts have been deleted.")


def qmod_topic_split(request, topic):
	post_ids = request.POST.getlist('posts_selected')
	if not post_ids:
		messages.error(request, "You haven't selected any post.")
		return
	if not 'confirmation' in request.POST:
		messages.info(request,
			"Are you sure you want to split selected posts?")
		return {
			'form': TopicNewForm()
		}
	form = TopicNewForm(request.POST)
	if form.is_valid():
		posts = Post.objects.filter(topic=topic, pk__in=post_ids)
		if topic.first_post_id in post_ids:
			posts.exclude(pk=topic.first_post_id)
		if not len(posts):
			return
		new_topic = form.save(commit=False)
		new_topic.created_by = posts[0].created_by
		new_topic.title = form.cleaned_data.get('title')
		new_topic.forum = topic.forum
		new_topic.save()
		posts.update(topic=new_topic)
		messages.success(request,
			"Selected posts have been splitted out of original topic.")
		return redirect(new_topic.get_absolute_url())
