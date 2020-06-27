"""
Django settings for alshamelah project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import datetime
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(SITE_ROOT, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = int(os.environ.get("DEBUG", default=0))

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

# Application definition

BASE_INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.sites',
    'django.contrib.postgres',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
]

INSTALLED_APPS = BASE_INSTALLED_APPS + [
    # Third-party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth',
    'rest_auth.registration',
    'crispy_forms',
    'debug_toolbar',
    'rolepermissions',
    # 'rest_framework_swagger',
    'easy_thumbnails',

    # Local
    'apps.categories',
    'apps.authors',
    'apps.books',
    'apps.users',
    'apps.support',
    'apps.chatrooms',
    'apps.sms',

    # file cleanup on model delete
    'django_cleanup.apps.CleanupConfig',
    'drf_yasg',
]

SITE_ID = 1
SITE_NAME = 'Al-Shamelah App'
SITE_DOMAIN = 'Al-Shamelah.com'

REST_USE_JWT = True
REST_SESSION_LOGIN = False

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
INTERNAL_IPS = [
    '127.0.0.1',
]
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 20
}
REST_REGISTRATION = {
    'REGISTER_VERIFICATION_ENABLED': True,
    'RESET_PASSWORD_VERIFICATION_ENABLED': True,
    'REGISTER_EMAIL_VERIFICATION_ENABLED': True,
    # 'REGISTER_VERIFICATION_URL': 'https://frontend-host/verify-user/',
    'RESET_PASSWORD_VERIFICATION_URL': 'https://frontend-host/reset-password/',
    'REGISTER_EMAIL_VERIFICATION_URL': 'https://frontend-host/verify-email/',

    'VERIFICATION_FROM_EMAIL': 'al-shamelah@internet-svc.com',
}

EMAIL_VERIFICATION = 'optional'
ACCOUNT_ADAPTER = 'apps.users.adapter.UserAdapter'
EMAIL_OTP_EXPIRY = 60 * 60
PHONE_OTP_EXPIRY = 60 * 5

# CUSTOM USER MODEL CONFIGS
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = 'users.User'

ROLEPERMISSIONS_MODULE = 'apps.users.roles'
# ROLEPERMISSIONS_REGISTER_ADMIN = True

REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'apps.users.serializers.LoginSerializer',
    'USER_DETAILS_SERIALIZER': 'apps.users.serializers.UserSerializer',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'apps.users.serializers.RegisterSerializer',
}
JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=12)
}
ACCOUNT_LOGOUT_ON_GET = False
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'EXCLUDE_URL_NAMES': ['rest_verify_email', 'rest_logout'],
    'api_version': '1',
    'relative_paths': True,
    'doc_expansion': 'none',
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

ROOT_URLCONF = 'alshamelah.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'alshamelah.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# http://whitenoise.evans.io/en/stable/django.html#add-compression-and-caching-support
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# DJANGO-CRISPY-FORMS CONFIGS
# ------------------------------------------------------------------------------
# https://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap4"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = False
EMAIL_HOST = 'mail.internet-svc.com'
EMAIL_HOST_USER = 'al-shamelah@internet-svc.com'
EMAIL_HOST_PASSWORD = 'J*Pb4ATyb4@_KCn8'
EMAIL_PORT = 8889
DEFAULT_FROM_EMAIL = 'al-shamelah@internet-svc.com'

# Twilio Keys
TWILIO_ACCOUNT_SID = 'AC1e118a01b05f894be3c76cab4334be3b'
TWILIO_AUTH_TOKEN = '758c7916964f29f8764abcca829e69ef'
TWILIO_NUMBER = '+15704131570'

# My Fatoorah
PAYMENT_TEST_URL = 'https://apitest.myfatoorah.com'
MYFATOORAH_TEST_API_KEY = '7Fs7eBv21F5xAocdPvvJ-sCqEyNHq4cygJrQUFvFiWEexBUPs4AkeLQxH4pzsUrY3Rays7GVA6SojFCz2DMLXSJVqk8NG-plK-cZJetwWjgwLPub_9tQQohWLgJ0q2invJ5C5Imt2ket_-JAlBYLLcnqp_WmOfZkBEWuURsBVirpNQecvpedgeCx4VaFae4qWDI_uKRV1829KCBEH84u6LYUxh8W_BYqkzXJYt99OlHTXHegd91PLT-tawBwuIly46nwbAs5Nt7HFOozxkyPp8BW9URlQW1fE4R_40BXzEuVkzK3WAOdpR92IkV94K_rDZCPltGSvWXtqJbnCpUB6iUIn1V-Ki15FAwh_nsfSmt_NQZ3rQuvyQ9B3yLCQ1ZO_MGSYDYVO26dyXbElspKxQwuNRot9hi3FIbXylV3iN40-nCPH4YQzKjo5p_fuaKhvRh7H8oFjRXtPtLQQUIDxk-jMbOp7gXIsdz02DrCfQIihT4evZuWA6YShl6g8fnAqCy8qRBf_eLDnA9w-nBh4Bq53b1kdhnExz0CMyUjQ43UO3uhMkBomJTXbmfAAHP8dZZao6W8a34OktNQmPTbOHXrtxf6DS-oKOu3l79uX_ihbL8ELT40VjIW3MJeZ_-auCPOjpE3Ax4dzUkSDLCljitmzMagH2X8jN8-AYLl46KcfkBV'
PAYMENT_URL = 'https://api.myfatoorah.com'
MYFATOORAH_API_KEY = 'tLdM_-f-n8W4PmD755_P4R3H9wyh3_Ky_TvDyZP2OZfODV8FkPR5jgMaIdUt0xvxxNcT9b13gX8ozRRecyKJPa_dIrbdFYdF6U97KCBYDvpjEOLcmJLxAdLPQOW96oLSF0RWVeJJrpu5fZbzscyk7bXm1BvvFI2R7rQgN1CE8lWdsotT6J7XvJQ0rzwPxAfNgx4uQR1pAG3VABcqY3ivz14vxG4RFB7buvy9IQLZSAoXv06qjPs1G3D8un2TKGYGMEPDcIKqFserOnL6lLZ5qLALXcLEhX9nBL4v_XOLmHsNoatHQxzpgabgrHoL9rZ_9sBlV-dPRoYVOPXN1DDXD2H2jlFFb0GZHl45uPxSbITaWiRgJHdj8OUjuXIte3R9ocE0LHmjvVtXzGbzXcTUYzR2QxesS_4QKN3UKt0Bs4jPgtb3NYKJZYmq5TPRDT4vfGmpOv1yWtwinQWZXGL_yAtXoOHKBTH7W9Gc2Wm2Ugc_4G53kBtTzG-UpodBvUgfFrVCj0q8DroUKGpHRRFIwAOljbT8ywkqMJQqUaWv3bhbZtLujhQQtVq_-C84dg_Cjtj9ggxpLQE-h9TbSTp5pGWjvFkeuvkRku3Z32S9bUmkgZhl4Nl7zvm-zWHqlcQUKna-LV7s56BN26KIAsnFSip3MrNZrxE5TukuW3C8mNH2WNSh'
# CALLBACK_URL=https://tutor-app-dev.dunice-testing.com/api/v1/payment/redirect-success
# ERROR_URL=https://tutor-app-dev.dunice-testing.com/api/v1/payment/redirect-fail

# LOGGING
# ------------------------------------------------------------------------------
# Default logging in https://github.com/django/django/blob/master/django/utils/log.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(name)s %(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'db_console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            "class": 'logging.NullHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['db_console'],
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'mail_admins'],
            'propagate': True
        },
        'py.warnings': {
            'handlers': ['null', ],
            'propagate': False
        },
        'oscar.alerts': {
            'handlers': ['null', ],
            'level': "INFO",
            'propagate': False
        },
        '': {
            'handlers': ['console', ],
            'level': "INFO",
        },
    }
}
