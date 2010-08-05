function voteup(post_id){
	if ($('post-' + post_id).down('a.karma_positive').hasClassName('current')) {
		return false;
	}
	$('post-' + post_id).down('span.karma-voted').update('<img src="/static/images/throbber.gif" />');
	Dajaxice.forums.voteup('Dajax.process', {'post_id': post_id});
	return false;
}

function votecancel(post_id){
	if ($('post-' + post_id).down('a.karma_neutral').hasClassName('current') == true) {
		return false;
	}
	$('post-' + post_id).down('span.karma-voted').update('<img src="/static/images/throbber.gif" />');
	Dajaxice.forums.votecancel('Dajax.process', {'post_id': post_id});
	return false;
}

function votedown(post_id){
	if ($('post-' + post_id).down('a.karma_negative').hasClassName('current') == true) {
		return false;
	}
	$('post-' + post_id).down('span.karma-voted').update('<img src="/static/images/throbber.gif" />');
	Dajaxice.forums.votedown('Dajax.process', {'post_id': post_id});
	return false;
}
