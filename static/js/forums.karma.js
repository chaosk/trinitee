function voteup(post_id){
	if ($('post-' + post_id).down('.karma_positive').hasClassName('current')) {
		return false;
	}
	$('post-' + post_id).down('.karma-box').setAttribute('title', 'Loading...');
	$('post-' + post_id).down('.karma-box').addClassName('tooltip');
	$('post-' + post_id).down('.karma-box').addClassName('tooltip-visible');
	Dajaxice.forums.voteup('Dajax.process', {'post_id': post_id});
	return false;
}

function votecancel(post_id){
	if ($('post-' + post_id).down('.karma_neutral').hasClassName('current')) {
		return false;
	}
	$('post-' + post_id).down('.karma-box').setAttribute('title', 'Loading...');
	$('post-' + post_id).down('.karma-box').addClassName('tooltip');
	$('post-' + post_id).down('.karma-box').addClassName('tooltip-visible');
	Dajaxice.forums.votecancel('Dajax.process', {'post_id': post_id});
	return false;
}

function votedown(post_id){
	if ($('post-' + post_id).down('.karma_negative').hasClassName('current')) {
		return false;
	}
	$('post-' + post_id).down('.karma-box').setAttribute('title', 'Loading...');
	$('post-' + post_id).down('.karma-box').addClassName('tooltip');
	$('post-' + post_id).down('.karma-box').addClassName('tooltip-visible');
	Dajaxice.forums.votedown('Dajax.process', {'post_id': post_id});
	return false;
}
