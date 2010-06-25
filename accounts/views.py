import datetime
from django.shortcuts import redirect, get_object_or_404
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext, loader, Context, Template
from accounts.models import ActivationKey, UserProfile
from accounts.forms import *
from utils.annoying.functions import get_config, get_object_or_None
from utils.annoying.decorators import render_to
from utils.annoying.utils import HttpResponseReload
from utils.internal.decorators import user_passes_test_or_403


@user_passes_test_or_403(lambda u: not u.is_active)
# Checking if current user is active is correct, as AnonymousUser
# is always not active and User with is_active=False cannot login.
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
					next = request.POST.get('next', '').strip()
					if next:
						return redirect(next)
					return redirect(reverse('accounts.views.profile_settings'))
				else:
					messages.error(request, "Your account is not active.")
			else:
				messages.error(request, "Your username and password \
					didn't match. Please try again.")
	else:
		form = LoginForm()
	return {'form': form, 'next': request.GET.get('next', '').strip()}


# collides with django.contrib.auth.logout
def logout_(request):
	logout(request)
	messages.success(request, "Logged out successfully.")
	return redirect(reverse('home'))


@render_to('accounts/userlist.html')
def userlist(request):
	users = cache.get('accounts_userlist')
	if users == None:
		users = User.objects.all().order_by('username').select_related('profile')
		cache.set('accounts_userlist', users)
	form = UserSearchForm(request.GET)
	users = form.filter(users)
	return {'users': users, 'form': form}


@login_required
@render_to('accounts/profile_settings.html')
def profile_settings(request):
	return {}


@login_required
@render_to('accounts/profile_settings_avatar.html')
def profile_settings_avatar(request):
	profile = UserProfile.objects.get(pk=request.user.id)
	if request.method == 'POST':
		form = SettingsAvatarForm(request.POST, request.FILES, instance=profile)
		if form.is_valid():
			if form.cleaned_data['delete']:
				profile.avatar.delete()
				profile.save()
				messages.success(request, "Successfully removed your avatar.")
			elif 'avatar' in request.FILES:
				profile = form.save(commit=False)
				profile.avatar.save('%s.png' % request.user.id, request.FILES['avatar'])
				profile.save()
				messages.success(request, "Saved.")
			return HttpResponseReload(request)
	else:
		form = SettingsAvatarForm(instance=profile)
	return {'form': form}


@login_required
@render_to('accounts/profile_settings_display.html')
def profile_settings_display(request):
	profile = UserProfile.objects.get(pk=request.user.id)
	if request.method == 'POST':
		form = SettingsDisplayForm(request.POST, instance=profile)
		if form.is_valid():
			form.save()
			messages.success(request, "Saved.")
	else:
		form = SettingsDisplayForm(instance=profile)
	return {'form': form}


@login_required
@render_to('accounts/profile_settings_identity.html')
def profile_settings_identity(request):
	if request.user.is_staff:
		profile_form_class = SettingsIdentityStaffForm
	else:
		profile_form_class = SettingsIdentityForm
	if request.method == 'POST':
		user_form = SettingsIdentityUserForm(request.POST, instance=request.user)
		profile_form = profile_form_class(request.POST, instance=request.user.profile)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			messages.success(request, "Saved.")
	else:
		user_form = SettingsIdentityUserForm(instance=request.user)
		profile_form = profile_form_class(instance=request.user.profile)
	return {'user_form': user_form, 'profile_form': profile_form}


@login_required
@render_to('accounts/profile_settings_signature.html')
def profile_settings_signature(request):
	profile = UserProfile.objects.get(pk=request.user.id)
	if request.method == 'POST':
		form = SettingsSignatureForm(request.POST, instance=profile)
		if form.is_valid():
			form.save()
			messages.success(request, "Saved.")
	else:
		form = SettingsSignatureForm(instance=profile)
	return {'form': form}


@render_to('accounts/profile_details.html')
def profile_details(request, user_id):
	user_details = cache.get('accounts_profile_%s' % user_id)
	if user_details == None:
		user_details = get_object_or_404(
			User.objects.select_related('profile'), pk=user_id)
		cache.set('accounts_profile_%s' % user_id, user_details)
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
				'server_name': request.get_host()})
			send_mail("E-mail activation at %s" % site_name, t.render(c),
				get_config('MAILER_ADDRESS', 'example@example.com'),
				[email], fail_silently=False)
			messages.success(request, "Thank you for registering. \
			An email has been sent to the specified address with \
			instructions on how to activate your new account. \
			If it doesn't arrive you can contact the forum \
			administrator at %s" % webmaster_email)
			return redirect(reverse('accounts.views.login_'))
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
			% reverse('accounts.views.new_activation_key'))
	else:
		user.is_active = True
		user.save()
		messages.success(request, "Your account has been activated.")
	activation.delete()
	return redirect(reverse('home'))


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
			return redirect(reverse('home'))
		if form.is_valid():
			t = loader.get_template('accounts/email/email_activation.html')
			ak = ActivationKey(user=user)
			ak.save()
			webmaster_email = get_config('WEBMASTER_EMAIL', 'example@example.com')
			site_name = get_config('SITE_NAME', 'Trinitee application')
			c = Context({'new_user': user, 'activation_key': ak.key,
				'webmaster_email': webmaster_email, 'site_name': site_name,
				'server_name': request.get_host()})
			send_mail("E-mail activation at %s" % site_name, t.render(c),
				get_config('MAILER_ADDRESS', 'example@example.com'),
				[email], fail_silently=False)
			messages.success(request, "An email has been sent \
			to the specified address with instructions on how to activate \
			your new account. If it doesn't arrive you can contact the forum \
			administrator at %s" % webmaster_email)
			return redirect(reverse('home'))
	else:
		form = ResendActivationKeyForm()
	return {'form': form}
