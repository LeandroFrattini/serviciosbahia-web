import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-solo-para-desarrollo-local')

DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

if 'RENDER' in os.environ:
    ALLOWED_HOSTS += [
        '.onrender.com',
        'serviciosbahia.com.ar',
        'www.serviciosbahia.com.ar',
    ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'profesionales',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'serviciosbahia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'serviciosbahia.wsgi.application'

if 'RENDER' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

_AWS_KEY    = os.environ.get('AWS_ACCESS_KEY_ID', '')
_AWS_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
_BUCKET     = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
_SUBDOMAIN  = os.environ.get('SUPABASE_SUBDOMAIN', '')

if 'RENDER' in os.environ and all([_AWS_KEY, _AWS_SECRET, _BUCKET, _SUBDOMAIN]):
    AWS_ACCESS_KEY_ID     = _AWS_KEY
    AWS_SECRET_ACCESS_KEY = _AWS_SECRET
    AWS_STORAGE_BUCKET_NAME = _BUCKET
    AWS_S3_ENDPOINT_URL   = f'https://{_SUBDOMAIN}.supabase.co/storage/v1/s3'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL       = 'public-read'
    AWS_QUERYSTRING_AUTH  = False
    AWS_S3_VERIFY         = True
    AWS_S3_ADDRESSING_STYLE = 'path'
    AWS_S3_REGION_NAME    = 'us-east-1'
    AWS_S3_CUSTOM_DOMAIN  = f'{_SUBDOMAIN}.supabase.co/storage/v1/object/public/{_BUCKET}'
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if 'RENDER' in os.environ
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ── MercadoPago ───────────────────────────────────────────────────────────────
MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN', 'TEST-7938861232797174-061022-e5dbb5f45a74f5ba48b5e9e20a0d9fdb-529282922')

# Datos para transferencias manuales (mostramos al usuario)
MP_CBU = os.environ.get('MP_CBU', '')
MP_ALIAS_CBU = os.environ.get('MP_ALIAS_CBU', '')
MP_TITULAR = os.environ.get('MP_TITULAR', 'Servicios Bahia')
