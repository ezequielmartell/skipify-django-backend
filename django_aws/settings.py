"""
Django settings for django_aws project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import environ
import os

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = FRONTEND_DIR.joinpath('django-aws-frontend')
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env_path = BASE_DIR / ".env"
if env_path.is_file():
    environ.Env.read_env(env_file=str(env_path))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="ewfi83f2ofee3398fh2ofno24f")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", default="*")]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'accounts',
    'api',
]

MIDDLEWARE = [
    'django_aws.middleware.health_check_middleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_aws.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [FRONTEND_DIR],
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

WSGI_APPLICATION = 'django_aws.wsgi.application'

if DEBUG:
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
else:
    CSRF_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SAMESITE = 'Strict'

CSRF_COOKIE_HTTPONLY = False  # False since we will grab it via universal-cookies
SESSION_COOKIE_HTTPONLY = True

# CORS_ALLOW_ALL_ORIGINS = DEBUG

# PROD ONLY
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", default=False)
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", default=False)

if "CSRF_TRUSTED_ORIGINS" in os.environ:
    CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(",")
# print(CSRF_TRUSTED_ORIGINS)

if "CORS_ALLOWED_ORIGINS" in os.environ:
    CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS").split(",")
# print(CORS_ALLOWED_ORIGINS)

CORS_ORIGIN_ALLOW_ALL = DEBUG
CORS_ALLOW_CREDENTIALS = DEBUG

DATABASES = {
    # 'default': env.db()
    'default': env.db(default="sqlite:///db.sqlite3")
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators 

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# # STATIC_URL = 'static/'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "static"
# STATICFILES_DIRS = (
#     FRONTEND_DIR.joinpath('build/static'),  # new
# )
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
AUTH_USER_MODEL = 'accounts.CustomUser'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="sqs://test:test@sqs:9324")
CELERY_TASK_DEFAULT_QUEUE = env("CELERY_TASK_DEFAULT_QUEUE", default="default")
CELERY_IMPORTS = (
'django_aws.tasks',
)
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": env("AWS_REGION", default="us-east-1")
}

CELERY_BEAT_SCHEDULE = {
    "beat_task": {
        "task": "django_aws.tasks.sync_boycott_tasks",
        "schedule": 60.0,
    },
}

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey' # this is exactly the value 'apikey'
EMAIL_HOST_PASSWORD = env('SENDGRID_API_KEY')
EMAIL_PORT = 587
EMAIL_USE_TLS = True