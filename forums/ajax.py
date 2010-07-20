from django.contrib.auth.decorators import login_required
from forums.models import Post
from forums.views import post_vote
from utilities.dajax.core import Dajax
from utilities.dajaxice.core import dajaxice_functions

""" The was no comment in this file until i wrote one. """

@login_required
def voteup(request, post_id):
	return vote(request, post_id, 1)
dajaxice_functions.register(voteup)

@login_required
def votedown(request, post_id):
	return vote(request, post_id, -1)
dajaxice_functions.register(votedown)

def vote(request, post_id, vote_value):
	result = post_vote(request, post_id, vote_value)
	dajax = Dajax()	
	if isinstance(result, Post):
		dajax.assign('#post-%s span.karma-voted' % post_id, 'innerHTML', 'Saved.')
		dajax.assign('#post-%s span.karma-count' % post_id, 'innerHTML', result.get_karma())
	else:
		dajax.assign('#post-%s span.karma-voted' % post_id, 'innerHTML', result[0])
	return dajax.json()