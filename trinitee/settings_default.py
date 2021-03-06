# pylint: disable-all
"""
settings_default.py

Do NOT (!!!) edit this file!
Please override settings in settings_local.py instead.
"""

import os
import sys
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
# Django settings for trinitee project.

PROJECT_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(os.path.join(PROJECT_DIR, "lib"), "vendor"))

DEBUG = False
TEMPLATE_DEBUG = False
TEMPLATE_CACHING = True

INTERNAL_IPS = ('127.0.0.1',)

ADMINS = (
#	('John Doe', 'joe@doe.com'),
)

MANAGERS = ADMINS

DATABASES = {
	'default': {
		# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3'.
		'ENGINE': 'django.db.backends.sqlite3',
		# Or path to database file if using sqlite3.
		'NAME': PROJECT_DIR + '/trinitee.sqlite',
		# Not used with sqlite3.
		'USER': '',
		# Not used with sqlite3.
		'PASSWORD': '',
		# Set to empty string for localhost. Not used with sqlite3.
		'HOST': '',
		# Set to empty string for default. Not used with sqlite3.
		'PORT': '',
	}
}

MAILER_ADDRESS = ''
WEBMASTER_EMAIL = ''


# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(MEDIA_ROOT, 'static')

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/media/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/static/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'foobar'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# User profile model
AUTH_PROFILE_MODULE = 'core.UserProfile'

ANONYMOUS_USER_ID = -1

# Message storage backend
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'

reverse_lazy = lazy(reverse, str)

ABSOLUTE_URL_OVERRIDES = {
	# 'auth.user': lambda u: reverse_lazy('profile', kwargs={'user_id': u.id}),
}

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
	'django.template.loaders.eggs.Loader',
)

if TEMPLATE_CACHING:
	TEMPLATE_LOADERS = (
		('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),
	)

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

AUTHENTICATION_BACKENDS = (
	'userena.backends.UserenaAuthenticationBackend',
	'guardian.backends.ObjectPermissionBackend',
	'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.middleware.http.ConditionalGetMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.transaction.TransactionMiddleware',
	'reversion.middleware.RevisionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'wiki.middleware.WikiWhitespaceMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.static',
	'django.core.context_processors.media',
	'django.core.context_processors.request',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
	os.path.join(PROJECT_DIR, 'templates'),
)

PROJECT_APPS = (
	'core',
	'lib',
	# 'accounts',
	'forums',
	'wiki',
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.admin',
	'guardian',
	'reversion',
	'south',
	'easy_thumbnails',
	'userena',
	'userena.contrib.umessages',
) + PROJECT_APPS

PYLINT_RCFILE = os.path.join(os.path.dirname(PROJECT_DIR), '.pylintrc')