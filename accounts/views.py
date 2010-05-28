from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from accounts.forms import UserForm

def profile_details(request):
	pass

def register(request):
	if request.method == 'POST':
		form = UserForm(request.POST)
		if form.is_valid():
			# FIXME actually _add_ user to database.
			messages.success(request, 'You have successfully created an account.')
			return redirect('/')
	else:
		form = UserForm()
	return render_to_response('accounts/register.html', { 'form': form }, context_instance=RequestContext(request))
			