from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import (authenticate, login as auth_login,
	logout as auth_logout)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.forms import LoginForm, RegisterForm
from annoying.decorators import render_to
from annoying.functions import get_config


@render_to('accounts/login.html')
def login(request):
	if request.user.is_authenticated():
		return redirect(reverse('home'))

	next_uri = request.REQUEST.get('next', get_config('LOGIN_REDIRECT_URL',
		reverse('home')))
	# rescuing poor users from infinite redirection loop
	if next_uri == get_config('LOGIN_URL', reverse('login')):
		next_uri = get_config('LOGIN_REDIRECT_URL', reverse('home'))

	form = LoginForm()

	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid() and form.user:
			auth_login(request, form.user)
			messages.success(request, "Hello, {0}.".format(form.user))
			return redirect(next_uri)

	return {
		'form': form,
		'next': next_uri,
	}


@login_required
def logout(request):
	next_uri = request.REQUEST.get('next', reverse('home'))
	auth_logout(request)
	messages.success(request, "Bye bye.")
	return redirect(next_uri)


@render_to('accounts/register.html')
def register(request):
	if request.user.is_authenticated():
		return redirect(reverse('home'))

	next_uri = request.REQUEST.get('next', reverse('home'))
	# rescuing poor users from infinite redirection loop
	if next_uri == get_config('LOGIN_URL', reverse('login')):
		next_uri = reverse('home')

	form = RegisterForm()

	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			if user is not None:
				auth_login(request, user)
				messages.success(request, "Welcome aboard, {0}.".format(user))
			return redirect(next_uri)

	return {
		'form': form,
		'next': next_uri,
	}


@render_to('accounts/profile.html')
def profile(request, user_id):
	user = get_object_or_404(User.objects.select_related(), pk=user_id)
	return {
		'profile_user': user,
	}


@render_to('accounts/list.html')
def userlist(request):
	return {
		'users': User.objects.all().select_related(),
	}
