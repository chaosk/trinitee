from django.contrib.auth.decorators import login_required
from forums.models import Post
from forums.views import post_vote
from utilities.dajax.core import Dajax
from utilities.dajaxice.core import dajaxice_functions

""" The was no comment in this file until I wrote one. """


@login_required
def voteup(request, post_id):
	return vote(request, post_id, 1)
dajaxice_functions.register(voteup)


@login_required
def votecancel(request, post_id):
	return vote(request, post_id, 0)
dajaxice_functions.register(votecancel)


@login_required
def votedown(request, post_id):
	return vote(request, post_id, -1)
dajaxice_functions.register(votedown)

CSS_CLASSES = {
	-1: 'negative',
	0: 'neutral',
	1: 'positive',
}

def vote(request, post_id, vote_value):
	result = post_vote(request, post_id, vote_value)
	dajax = Dajax()
	if isinstance(result, Post):
		dajax.remove_css_class('#post-%s .karma' % post_id, 'current')
		dajax.add_css_class('#post-%s .karma_%s' % (post_id, CSS_CLASSES[vote_value]), 'current')
		dajax.add_css_class('#post-%s .karma-box' % post_id, ('tooltip', 'tooltip-visible'))
		dajax.assign('#post-%s .karma-box' % post_id, 'title', "Saved.")
		dajax.assign('#post-%s .karma-count' % post_id, 'innerHTML',
			result.get_karma())
	else:
		dajax.add_css_class('#post-%s .karma-box' % post_id, ('tooltip', 'tooltip-visible'))
		dajax.assign('#post-%s .karma-box' % post_id, 'title', result[0])
	return dajax.json()
