function voteup(post_id){
	$('post-' + post_id).down('span.karma-voted').update('<img src="/static/images/throbber.gif" />');
	Dajaxice.forums.voteup('Dajax.process', {'post_id': post_id});
	return false;
}

function votecancel(post_id){
	$('post-' + post_id).down('span.karma-voted').update('<img src="/static/images/throbber.gif" />');
	Dajaxice.forums.votecancel('Dajax.process', {'post_id': post_id});
	return false;
}

function votedown(post_id){
	$('post-' + post_id).down('span.karma-voted').update('<img src="/static/images/throbber.gif" />');
	Dajaxice.forums.votedown('Dajax.process', {'post_id': post_id});
	return false;
}
