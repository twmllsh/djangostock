"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import sys
from pathlib import Path
from environ import Env
MYENV = Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# 자체적으로 docker compose 에 의해 환경변수가 설정되었으니 파일로 읽어오지 않아도 된다. 
# ENV_PATH = BASE_DIR / ".env"
# if ENV_PATH.exists():
#     with ENV_PATH.open(encoding="utf-8") as f:
#         MYENV.read_env(f, overwrite=True)
# else:
#     print(":", ENV_PATH, file=sys.stderr)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-fun(cn@#4i9x*pv#tgikx#6@d1o)c05g24!3mv*05+lpjryr#1'
SECRET_KEY = MYENV.str(
    "SECRET_KEY",
    default='django-insecure-fun(cn@#4i9x*pv#tgikx#6@d1o)c05g24!3mv*05+lpjryr#1',
)
# SECURITY WARNING: don't run with debug turned on in production!

# DEBUG = True
DEBUG = MYENV.bool("DEBUG", default=True) ## DEBUG 값이 있으면 가져오고 아니면 True값
# DEBUG = MYENV.bool("DEBUG", default=False) ## DEBUG 값이 있으면 가져오고 아니면 True값
if DEBUG:
    print("###########################################")
    print("DEBUG 모드 작동!! ")
    print("###########################################")
else:
    print("###########################################")
    print("실제 서버 작동")
    print("###########################################")
# ALLOWED_HOSTS = []
ALLOWED_HOSTS = MYENV.list("ALLOWED_HOSTS", default=["*"])

# Application definition

INSTALLED_APPS = [
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third apps
    'django_apscheduler',
    'django_bootstrap5',
    "django_extensions",
    "template_partials",
    # local apps
    'core',
    'dashboard',
    'ex_form',
    
]

# 로그인 후 리다이렉트할 URL 설정
# LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar"
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    ] + MIDDLEWARE

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
import pymysql
pymysql.install_as_MySQLdb()

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': MYENV.str("POSTGRES_DB", default="stock"),
            'USER': MYENV.str("POSTGRES_USER", default="sean"),
            'PASSWORD': MYENV.str("POSTGRES_PASSWORD", default="2402"),
            'HOST': MYENV.str("POSTGRES_HOST", default="db"),
            'PORT': 5432,
        },
        'mysql': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': "mysql_db",
            'USER': "mysql_user",
            'PASSWORD': "mysql_pw",
            'HOST': "mysql",
            'PORT': "33061",
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            # 'NAME': "stock",
            'NAME': MYENV.str("POSTGRES_DB", default="stock"),
            'USER': "sean",
            'PASSWORD': "2402",
            'HOST': 'db',
            'PORT': 5432,
        },
        'mysql': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': "mysql_db",
            'USER': "mysql_user",
            'PASSWORD': "mysql_pw",
            'HOST': "mysql",
            'PORT': "33061",
        }
    }




# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = MYENV.str("LANGUAGE_CODE", default="ko-kr")

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# 정적 파일이 수집될 디렉토리
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# django-debug-toolbar 허용 ip
# INTERNAL_IPS = ["127.0.0.1"]
INTERNAL_IPS = MYENV.list("INTERNAL_IPS", default=["127.0.0.1"])

SHELL_PLUS_IMPORTS = [
    'from dashboard.utils.dbupdater import GetData, DBUpdater',
    'import random',
    'import time',
    'import asyncio',
    'import pickle',
    'import pandas as pd',
    'import pandas_ta as ta',
    'import FinanceDataReader as fdr',
    'from dashboard.utils.mystock import Stock, ElseInfo',
    'from dashboard.utils import chart', 
    # 추가적인 임포트도 여기에 나열
]

SCHEDULER_DEFAULT = True   ## https://velog.io/@jwun95/Django-Scheduler%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%B4%EB%B3%B4%EC%9E%90
