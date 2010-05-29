from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from accounts.models import UserProfile
from accounts.forms import LoginForm, RegistrationForm

# collides with django.contrib.auth.login
def login_(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					messages.success(request, 'Logged in successfully.')
					return redirect('/accounts/profile/')
				else:
					messages.error(request, 'Your account is not active.')
			else:
				messages.error(request, 'Your username and password didn\'t match. Please try again.')
	else:
		form = LoginForm()
	return render_to_response('accounts/login.html', {'form': form}, context_instance=RequestContext(request))

# collides with django.contrib.auth.logout
def logout_(request):
	logout(request)
	messages.success(request, 'Logged out successfully.')
	return redirect('/')

@login_required
def profile_index(request):
	return render_to_response('accounts/profile_index.html', context_instance=RequestContext(request))

@login_required
def profile_edit(request):
	return render_to_response('accounts/profile_edit.html')

def profile_details(request, user_id):
	user_details = get_object_or_404(User, id=user_id)
	return render_to_response('accounts/profile_details.html', {'user_details': user_details}, context_instance=RequestContext(request))

def register(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			email = form.cleaned_data['email']
			user = User(username=username, password=password, email=email, is_active=False)
			user.save()
			# TODO send verification e-mail
			messages.success(request, 'Thank you for registering. An email has been sent to the specified address with instructions on how to activate your new account. If it doesn\'t arrive you can contact the forum administrator at %s' % WEBMASTER_EMAIL)
			return redirect('/')
	else:
		form = RegistrationForm()
	return render_to_response('accounts/register.html', {'form': form}, context_instance=RequestContext(request))
			