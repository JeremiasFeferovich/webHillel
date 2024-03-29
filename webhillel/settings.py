"""
Django settings for webhillel project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "+k!@)$demq7!z@dlf4hk0jiy=z3l3_d)&cx4hxhtc^u85ps_rj"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["www.hillelargentina.org.ar", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "registration.apps.RegistrationConfig",
    "location.apps.LocationConfig",
    "profiles.apps.ProfilesConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ckeditor",
    "core",
    "pages.apps.PagesConfig",
    "social.apps.SocialConfig",
]
AUTHENTICATION_BACKENDS = [
    "registration.backends.EmailVerifiedBackend",
]


if DEBUG:
    SITE_ID = 2
else:
    SITE_ID = 3

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": BASE_DIR / "backup"}


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.gzip.GZipMiddleware",  # gzip
]

ROOT_URLCONF = "webhillel.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "registration.processors.ctx_dict",
                "social.processors.ctx_dict",
                "profiles.processors.ctx_dict",
            ],
        },
    },
]

WSGI_APPLICATION = "webhillel.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "es"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATE_FORMAT = "d-m-Y"


# Login Redirect
LOGIN_REDIRECT_URL = "home"  # 'pages:pages'
LOGOUT_REDIRECT_URL = "home"


# emails
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_FILE_PATH = BASE_DIR / "send_emails"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_HOST_USER = "infohillel@gmail.com"
    EMAIL_HOST_PASSWORD = "zftsqbzhgeuqmzrz"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
else:
    # Aqui hay que configurar un email real para producción
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_FILE_PATH = BASE_DIR / "send_emails"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_HOST_USER = "infohillel@gmail.com"
    EMAIL_HOST_PASSWORD = "zftsqbzhgeuqmzrz"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

    pass


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
