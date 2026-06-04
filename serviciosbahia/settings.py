import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'serviciosbahia-dev-key-cambiar-en-produccion'

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
if 'RENDER' in os.environ:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if 'RENDER' in os.environ:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    SUBDOMAIN = os.environ.get('SUPABASE_SUBDOMAIN', '')
    if all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME]):
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        AWS_S3_ENDPOINT_URL = f'https://{SUBDOMAIN}.supabase.co/storage/v1/s3'
        AWS_S3_SIGNATURE_VERSION = 's3v4'
        AWS_S3_FILE_OVERWRITE = False
        AWS_DEFAULT_ACL = None
        AWS_QUERYSTRING_AUTH = False
        AWS_S3_VERIFY = True
        AWS_S3_ADDRESSING_STYLE = 'path'
        AWS_S3_REGION_NAME = 'us-east-1'
        AWS_S3_CUSTOM_DOMAIN = f'{SUBDOMAIN}.supabase.co/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}'

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'