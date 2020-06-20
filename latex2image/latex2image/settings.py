from __future__ import absolute_import

"""
Django settings for latex2image project.

Generated by 'django-admin startproject' using Django 2.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.conf.global_settings import STATICFILES_FINDERS, gettext_noop

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# We put it in a subdir so that we can map it in docker with -v param.
_local_settings_file = os.path.join(BASE_DIR, "local_settings", "local_settings.py")

if os.environ.get("L2I_LOCAL_TEST_SETTINGS", None):
    # This is to make sure local_settings.py is not used for unit tests.
    assert _local_settings_file != os.environ["L2I_LOCAL_TEST_SETTINGS"]
    _local_settings_file = os.environ["L2I_LOCAL_TEST_SETTINGS"]

local_settings = None
if os.path.isfile(_local_settings_file):
    local_settings_module = None
    local_settings_module_name, ext = (
        os.path.splitext(os.path.split(_local_settings_file)[-1]))
    assert ext == ".py"
    exec("from local_settings import %s as local_settings_module" % local_settings_module_name)

    local_settings = local_settings_module.__dict__  # type: ignore  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# https://stackoverflow.com/a/39252623/3437454
# You should override this in local_settings/local_settings.py
SECRET_KEY = 'v3i#)=ab)8zfqj%!)#nisqyi69jo@@h!0!x1r2&h65d&z6(56u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('L2I_DEBUG', 'off') == 'on'
# {{{ ALLOWED_HOSTS

ALLOWED_HOSTS = ("127.0.0.1",)

# You can set extra allowed host items by setting the item name
# startswith L2I_CORS_ALLOWED_HOST_ (with no ending 'S')
# e.g., L2I_ALLOWED_HOSTS_CAT = "http://example.com"
custom_allowed_hosts = [
    item for item in list(dict(os.environ).keys())
    if item.startswith("L2I_ALLOWED_HOST")]

if custom_allowed_hosts:
    ALLOWED_HOSTS = ALLOWED_HOSTS + tuple(custom_allowed_hosts)


# }}}

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_FINDERS += ("npm.finders.NpmFinder",)

STATICFILES_DIRS = (
        os.path.join(BASE_DIR, "latex2image", "static"),
        )

ADMIN_SITE_HEADER = gettext_noop("Latex2Image Admin")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "crispy_forms",
    "latex.apps.LatexConfig",
    # CORS
    'corsheaders',
    'rest_framework.authtoken',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'latex2image.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["latex2image/templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'latex2image.wsgi.application'


# {{{ Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # },
    'default': {
        'ENGINE': 'djongo',
        'NAME': os.environ.get("LATEX_MONGO_DB_NAME", 'latex2image'),
        # 'CLIENT':
        #     {
        #         'host': os.environ.get("L2I_MONGODB_HOST", 'localhost'),
        #         'port': int(os.environ.get("L2I_MONGODB_PORT", 27017)),
        #         'username': os.environ.get("L2I_MONGODB_USERNAME", "admin"),
        #         'password': os.environ.get("L2I_MONGODB_PASSWORD", "password"),
        #      }
    }
}

client = {}

# The attribute of LatexImage object to be cached, the key is "tex_key" attribute.
# valid values are 'image', `data_url`. if set 'image', the absolute url of image
# will be cached. CompileError will be cached with cache key tex_key + "_error".
# If not set, no cache will be used.
L2I_API_CACHE_FIELD = "image"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

L2I_CACHE_MAX_BYTES = 65536

# For Mac as the host, set "-e L2I_MONGODB_PORT=docker.for.mac.host.internal"
# https://stackoverflow.com/a/45002996/3437454
mongo_host = os.environ.get("L2I_MONGODB_HOST", "host.docker.internal")
if mongo_host:
    client["host"] = mongo_host
mongo_port = os.environ.get("L2I_MONGODB_PORT", None)
if mongo_port:
    client.setdefault("host", "localhost")
    client["port"] = mongo_port
mongo_user = os.environ.get("L2I_MONGODB_USERNAME", None)
mongo_pwd = os.environ.get("L2I_MONGODB_PASSWORD", None)
if mongo_user and mongo_pwd:
    client["username"] = mongo_user
    client["password"] = mongo_pwd

if client and DATABASES["default"]["ENGINE"] == "djongo":
    DATABASES["default"]["CLIENT"] = client

# Execute the following in mongo cmdline:
# > use latex2image
# switched to db latex2image
# > db.createUser({user:"admin", pwd: "password", roles: [{role: "readWrite", db:"latex2image"}]})
# Successfully added user: {
#         "user" : "admin",
#         "roles" : [
#                 {
#                         "role" : "readWrite",
#                         "db" : "latex2image"
#                 }
#         ]
# }


# }}}


# {{{ Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

if os.environ.get("L2I_ENABLE_PASSWORD_VALIDATORS", False):
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

# }}}

LOGIN_REDIRECT_URL = 'home'

# {{{ CORS settings
# CORS_ORIGIN_ALLOW_ALL: If True, all origins will be accepted (not use the whitelist below). Defaults to False.
# CORS_ORIGIN_WHITELIST: List of origins that are authorized to make cross-site HTTP requests. Defaults to []
CORS_ORIGIN_ALLOW_ALL = os.environ.get("L2I_CORS_ORIGIN_ALLOW_ALL", None) is None
CORS_ORIGIN_WHITELIST = (
    'http://localhost:8020',
    'http://host.docker.internal:8020',
)

CORS_URLS_REGEX = r'^/api/.*$'

# You can set extra whitelist items by setting the item name
# startswith L2I_CORS_ORIGIN_WHITELIST
# e.g., L2I_CORS_ORIGIN_WHITELIST_LOCAL = "http://192.168.50.1"
custom_whitelist_items = [
    item for item in list(dict(os.environ).keys())
    if item.startswith("L2I_CORS_ORIGIN_WHITELIST")]

if custom_whitelist_items:
    CORS_ORIGIN_WHITELIST = CORS_ORIGIN_WHITELIST + tuple(custom_whitelist_items)

# }}}

# {{{ rest auth

# https://stackoverflow.com/a/52347668/3437454
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

# }}}


# {{{ Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = os.environ.get("L2I_LANGUAGE_CODE", 'en-us')

TIME_ZONE = os.environ.get("L2I_TZ", 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

# }}}

LOGIN_URL = "/login/"

# {{{ Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# }}}

CRISPY_TEMPLATE_PACK = "bootstrap3"


# {{{ override this if you are using, for example, s3 storage
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR + "/"

# DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
# }}}


if local_settings is not None:
    for name, val in local_settings.items():
        if not name.startswith("_"):
            globals()[name] = val

    # enable auto-reload
    try:
        import local_settings  # noqa
    except ImportError:
        pass