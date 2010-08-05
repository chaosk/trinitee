Event.observe(window, 'load', function() {
	$$('.posts_selected').invoke('observe', 'click', function(event) {
		if (this.checked) {
			$(this).up('tr', 1).addClassName('selected_post');
		}
		else {
			$(this).up('tr', 1).removeClassName('selected_post');
		}
	});
});