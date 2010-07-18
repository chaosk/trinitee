from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from forums.models import Post
from forums.views import post_vote
from utilities.dajax.core import Dajax
from utilities.dajaxice.core import dajaxice_functions

@login_required
def voteup(request, post_id):
	result = post_vote(request, post_id, 1)
	dajax = Dajax()
	if isinstance(result, Post):
		dajax.script('vote_saved(%i, %i);' % (post_id, result.get_karma()))
	else:
		dajax.script('vote_error(%i, "%s");' % (post_id, result[0]))
	return dajax.json()
dajaxice_functions.register(voteup)

@login_required
def votedown(request, post_id):
	result = post_vote(request, post_id, -1)
	dajax = Dajax()
	if isinstance(result, Post):
		dajax.script('vote_saved(%i, %i);' % (post_id, result.get_karma()))
	else:
		dajax.script('vote_error(%i, "%s");' % (post_id, result[0]))
	return dajax.json()
dajaxice_functions.register(votedown)