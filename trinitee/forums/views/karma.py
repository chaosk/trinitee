from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from forums.models import Post, PostKarma

KARMA_VALUES = {
	'down': -1,
	'revoke': 0,
	'up': 1,
}


@login_required
def karma_vote(request, post_id, action):
	if not request.user.has_perm('accounts.userprofile_karma'):
		raise Http403
	post = get_objects_or_404(Post, pk=post_id)

	try:
		value = KARMA_VALUES[action]
	except KeyError:
		if request.is_ajax():
			return False
		else:
			messages.error(request, "Invalid karma action.")
			return redirect(post.get_absolute_url())

	karma, created = PostKarma.objects.get_or_create(user=request.user,
		post=post, initial={'karma': value})
	if not created:
		karma.save()

	if request.is_ajax():
		# current karma?
		return True
	else:
		messages.success(request, "Successfully updated karma of selected post.")
		return redirect(post.get_absolute_url())
