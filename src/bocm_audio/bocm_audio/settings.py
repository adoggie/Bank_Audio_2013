# Django settings for audio project.
#--coding:utf-8--

import os,sys,os.path
HERE = os.path.abspath(os.path.dirname(__file__))#os.path.dirname(__file__)
PROJECT_PACKAGE = os.path.basename(HERE)
PROJECT_DIR=os.path.split(HERE)[0]



DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'audio',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'ffmpeg',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'



SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
# USE_TZ = True
USE_TZ = False

# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = os.path.join(PROJECT_DIR ,'media').replace('\\','/')
MEDIA_ROOT = 'c:/temp/audio'
if sys.platform.find('linux')!=-1:
	MEDIA_ROOT='/svr/temp'
	if not os.path.exists(MEDIA_ROOT):
		os.mkdir(MEDIA_ROOT)
	
	
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT =os.path.join(PROJECT_DIR , 'static_all').replace('\\','/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
	os.path.join(PROJECT_DIR , 'audio/static').replace('\\','/'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'jeyn^!&amp;vpo&amp;gy^m7z$#d0vj!)tc(&amp;5zyrrdyyeiy32q2-*!)(&amp;'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


#ROOT_URLCONF = 'bocm_audio.bocm_audio.urls'
ROOT_URLCONF = 'bocm_audio.urls'


# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bocm_audio.wsgi.application'

TEMPLATE_DIRS = (
	os.path.join(PROJECT_DIR, 'audio/templates').replace('\\','/'),
	#    os.path.join(os.path.dirname(__file__), 'polls/templates').replace('\\','/'),
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'audio',
	'storeadapter'
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

####################################logging config#########################################################
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'audio_formatters': {
			'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
		},
	},
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'class': 'django.utils.log.AdminEmailHandler'
	},
	'audio_handler': {
		'level': 'DEBUG',
		'filename':'logs/audio.log',
		'class': 'logging.handlers.RotatingFileHandler',
		'formatter':'audio_formatters',
		}
	},

	'loggers': {
		'django.request': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': True,
			},
		'audio_logger': {
			'handlers': ['audio_handler'],
			'level': 'DEBUG',
			'propagate': True,
		},
		}
}
####################################logging config#########################################################
if sys.platform.find('linux')!=-1:
	LOGGING['handlers']['audio_handler']['filename'] ='/svr/audio.log'


CONFIG_DIR = os.path.join(PROJECT_DIR , 'conf').replace('\\','/')

############
# SESSIONS #
############

SESSION_COOKIE_NAME = 'sessionid'                       # Cookie name. This can be whatever you want.
SESSION_COOKIE_AGE = 60*60*12  #60 * 60 * 24 * 7 * 2               # Age of cookie, in seconds (default: 2 weeks).
SESSION_COOKIE_DOMAIN = None                            # A string like ".lawrence.com", or None for standard domain cookie.
SESSION_COOKIE_SECURE = False                           # Whether the session cookie should be secure (https:// only).
SESSION_COOKIE_PATH = '/'                               # The path of the session cookie.
SESSION_COOKIE_HTTPONLY = True                          # Whether to use the non-RFC standard httpOnly flag (IE, FF3+, others)
SESSION_SAVE_EVERY_REQUEST = False                      # Whether to save the session data on every request.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True                 # Whether a user's session cookie expires when the Web browser is closed.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # The module to store session data
SESSION_FILE_PATH = None                                # Directory to store session files if using the file session module. If None, the backend will use a sensible default.
