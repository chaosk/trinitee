function toggle_editor(){
	if(!$('drawboard-div').hasClassName('editing')){
		$('drawboard-div').addClassName('editing');
		$('drawboard-div').hide();
		$('drawboard').show();
		$('drawboard-tools').show();
	}
}

function cancel_edit(){
	$('drawboard').hide();
	$('drawboard-div').removeClassName('editing');
	$('drawboard-div').show();
	$('drawboard-tools').hide();
}

function save(){
	new_content = $F('drawboard');
	$('drawboard').update("saving...");
	$('drawboard').readOnly = true;
	Dajaxice.misc.drawboard_save('Dajax.process', {'new_content': new_content});
}

function finish(){
	cancel_edit();
	$('drawboard').readOnly = false;
}