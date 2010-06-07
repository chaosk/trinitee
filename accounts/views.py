import datetime
from django.shortcuts import redirect, get_object_or_404
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext, loader, Context, Template
from accounts.models import ActivationKey
from accounts.forms import LoginForm, RegistrationForm, ResendActivationKeyForm, \
	SettingsAvatarForm, SettingsDisplayForm, SettingsIdentityForm, SettingsSignatureForm
from utils.annoying.functions import get_config, get_object_or_None
from utils.annoying.decorators import render_to
from utils.decorators import user_passes_test_or_403

# Checking if current user is active is correct, as AnonymousUser
# is always not active and User with is_active=False cannot login.
@user_passes_test_or_403(lambda u: not u.is_active)
@render_to('accounts/login.html')
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
					messages.success(request, "Logged in successfully.")
					return redirect(reverse('trinitee.accounts.views.profile_settings'))
				else:
					messages.error(request, "Your account is not active.")
			else:
				messages.error(request, "Your username and password \
					didn't match. Please try again.")
	else:
		form = LoginForm()
	return {'form': form}

# collides with django.contrib.auth.logout
def logout_(request):
	logout(request)
	messages.success(request, "Logged out successfully.")
	return redirect('/')

@login_required
@render_to('accounts/profile_settings.html')
def profile_settings(request):
	return {}

@login_required
@render_to('accounts/profile_settings_avatar.html')
def profile_settings_avatar(request):
	if request.method == 'POST':
		form = SettingsAvatarForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Saved.")
	else:
		form = SettingsAvatarForm()
	return {'form': form}

@login_required
@render_to('accounts/profile_settings_display.html')
def profile_settings_display(request):
	if request.method == 'POST':
		form = SettingsDisplayForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Saved.")
	else:
		form = SettingsDisplayForm()
	return {'form': form}

@login_required
@render_to('accounts/profile_settings_identity.html')
def profile_settings_identity(request):
	if request.method == 'POST':
		form = SettingsIdentityForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Saved.")
	else:
		form = SettingsIdentityForm()
	return {'form': form}

@login_required
@render_to('accounts/profile_settings_signature.html')
def profile_settings_signature(request):
	if request.method == 'POST':
		form = SettingsSignatureForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Saved.")
	else:
		form = SettingsSignatureForm()
	return {'form': form}

@render_to('accounts/profile_details.html')
def profile_details(request, user_id):
	user_details = get_object_or_404(User, pk=user_id)
	return {'user_details': user_details}

# ref: comment to accounts.views.login_
@user_passes_test_or_403(lambda u: not u.is_active)
@render_to('accounts/register.html')
def register(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			email = form.cleaned_data['email']
			user = User(username=username, email=email, is_active=False)
			user.set_password(password)
			user.save()
			t = loader.get_template('accounts/email/email_activation.html')
			ak = ActivationKey(user=user)
			ak.save()
			webmaster_email = get_config('WEBMASTER_EMAIL', 'example@example.com')
			site_name = get_config('SITE_NAME', 'Trinitee application')
			c = Context({'new_user': user, 'activation_key': ak.key,
				'webmaster_email': webmaster_email, 'site_name': site_name,
				'server_name': request.get_host() })
			send_mail("E-mail activation at %s" % site_name, t.render(c),
				get_config('MAILER_ADDRESS', 'example@example.com'),
				[email], fail_silently=False)
			messages.success(request, "Thank you for registering. \
			An email has been sent to the specified address with \
			instructions on how to activate your new account. \
			If it doesn't arrive you can contact the forum \
			administrator at %s" % webmaster_email)
			return redirect(reverse('trinitee.accounts.views.login_'))
	else:
		form = RegistrationForm()
	return {'form': form}

@user_passes_test_or_403(lambda u: not u.is_active)
def activate_account(request, user_id, activation_key):
	user = get_object_or_404(User, pk=user_id)
	activation = get_object_or_404(ActivationKey, user=user,
		key=activation_key)
	if activation.expires_at < datetime.datetime.now():
		messages.error(request, "Activation key has expired. \
			You can request a new key <a href=\"%s\">here</a>."
			% reverse('trinitee.accounts.views.new_activation_key'))
	else:
		user.is_active = True
		user.save()
		messages.success(request, "Your account has been activated.")
	activation.delete()
	return redirect('/')

@user_passes_test_or_403(lambda u: not u.is_active)
@render_to('accounts/resend_activation_key.html')
def resend_activation_key(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	activation = get_object_or_None(ActivationKey, user=user)
	if not activation == None:
		# Cleaning database from unused objects
		activation.delete()
	if request.method == 'POST':
		form = ResendActivationKeyForm(request.POST)
		if not form.cleaned_data['email'] == user.email:
			messages.error(request, "E-mail address sent by you doesn't match \
			with address used to register this account.")
			return redirect('/')
		if form.is_valid():
			t = loader.get_template('accounts/email/email_activation.html')
			ak = ActivationKey(user=user)
			ak.save()
			webmaster_email = get_config('WEBMASTER_EMAIL', 'example@example.com')
			site_name = get_config('SITE_NAME', 'Trinitee application')
			c = Context({'new_user': user, 'activation_key': ak.key,
				'webmaster_email': webmaster_email, 'site_name': site_name,
				'server_name': request.get_host() })
			send_mail("E-mail activation at %s" % site_name, t.render(c),
				get_config('MAILER_ADDRESS', 'example@example.com'),
				[email], fail_silently=False)
			messages.success(request, "An email has been sent \
			to the specified address with instructions on how to activate \
			your new account. If it doesn't arrive you can contact the forum \
			administrator at %s" % webmaster_email)
			return redirect('/')
	else:
		form = ResendActivationKeyForm()
	return {'form': form}