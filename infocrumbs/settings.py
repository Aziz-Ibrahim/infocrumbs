"""
Django settings for infocrumbs project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import os

if os.path.exists('env.py'):
    import env


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-m&om&9$k0u*tu+eaz6ydz=ie9e!+-d4u%o$n+(=jh@=o7f+mtw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # required by allauth

    #Third-party apps
    'allauth',
    'allauth.account',
    'crispy_forms',
    'crispy_bootstrap5',

    # Custom apps
    'accounts',
    'core',
    'checkout',
    'crumbs',
    'feedback',
    'pipeline',
    'preferences',
    'subscriptions',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # default
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth
]


SITE_ID = 1

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_METHODS = {'username', 'email'}  # Set of allowed login methods
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSignupForm'
}
ACCOUNT_EMAIL_VERIFICATION = 'none'

CRISPY_ALLOWED_TEMPLATE_PACK = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'infocrumbs.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'infocrumbs.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Stripe

STRIPE_CURRENCY = 'gbp'
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WH_SECRET', '')

# Stripe price lookup table
STRIPE_PRICE_LOOKUP = {
    'basic_weekly': 'price_123abcBasicWeek',
    'basic_monthly': 'price_456abcBasicMonth',
    'basic_annually': 'price_789abcBasicYear',
    'premium_weekly': 'price_123xyzPremiumWeek',
    'premium_monthly': 'price_456xyzPremiumMonth',
    'premium_annually': 'price_789xyzPremiumYear',
}

# API keys for external services

# Hugging Face API
HF_API_URL = os.environ.get('HF_API_URL')
HF_API_TOKEN = os.environ.get('HF_API_TOKEN')

# News & Media APIs
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
NEWS_API_URL = os.environ.get('NEWS_API_URL')

# Music
LASTFM_API_KEY = os.environ.get('LASTFM_API_KEY')
LASTFM_API_URL = os.environ.get('LASTFM_API_URL')

# Finance
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
ALPHA_VANTAGE_API_URL = os.environ.get('ALPHA_VANTAGE_API_URL')

FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY')
FINNHUB_API_URL = os.environ.get('FINNHUB_API_URL')

# Ninja API
APININJA_API_KEY = os.environ.get('APININJA_API_KEY')
APININJA_API_URL = os.environ.get('APININJA_API_URL')

# Sports
THENEWS_API_KEY = os.environ.get('THENEWSAPI_API_KEY')
THENEWSAPI_SPORTS_URL = os.environ.get('THENEWSAPI_SPORTS_URL')

SPORTS_API_KEY = os.environ.get('SPORTS_API_KEY')
SPORTMONKS_API_KEY = os.environ.get('SPORTMONKS_API_KEY')
SPORTMONKS_API_URL = os.environ.get('SPORTMONKS_API_URL')

# Gardeining / Plants
PARENUAL_API_KEY = os.environ.get('PARENUAL_API_KEY')
PARENUAL_API_URL = os.environ.get('PARENUAL_API_URL')

TREFLE_API_KEY = os.environ.get('TREFLE_API_KEY')
TREFLE_API_URL = os.environ.get('TREFLE_API_URL')

PERMAPEOPLE_KEY_ID = os.environ.get('PERMAPEOPLE_KEY_ID')
PERMAPEOPLE_KEY_SECRET = os.environ.get('PERMAPEOPLE_KEY_SECRET')
PERMAPEOPLE_API_URL = os.environ.get('PERMAPEOPLE_API_URL')

# Trivia / Fun
USELESS_FACTS_API_URL = os.environ.get('USELESS_FACTS_API_URL')
CHUCKNORRIS_API_URL = os.environ.get('CHUCKNORRIS_API_URL')

# Food / Drink
SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY')
SPOONACULAR_API_URL = os.environ.get('SPOONACULAR_API_URL')

# Technology
MEDIASTACK_API_KEY = os.environ.get("MEDIASTACK_API_KEY")
MEDIASTACK_TECHNOLOGY_URL = os.environ.get("MEDIASTACK_TECHNOLOGY_URL")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

