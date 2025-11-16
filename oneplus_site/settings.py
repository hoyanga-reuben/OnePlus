from pathlib import Path
import os
import pymysql

# MySQL support
pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

# ===================== SECURITY =====================
SECRET_KEY = 'django-insecure-a1w%y*p!tw^3#h1%@ynm)h2zoge*vcsxlw97s#%0x187^x9@mz'
DEBUG = False

# Allowed hosts (update after hosting)
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".pythonanywhere.com",
]

# Custom user model
AUTH_USER_MODEL = "content.CustomUser"

# ===================== INSTALLED APPS =====================
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Background Tasks
    'django_crontab',

    # Project apps
    'main',
    'content',

    # Third-party apps
    'django_ckeditor_5',
    'imagekit',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'widget_tweaks',
]

# ===================== MIDDLEWARE =====================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'oneplus_site.urls'

# ===================== TEMPLATES =====================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = 'oneplus_site.wsgi.application'

# ===================== DATABASE =====================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Reuben1998$oneplusresilence_DB',    # Your DB name in PythonAnywhere
        'USER': 'Reuben1998',                    # Replace with PythonAnywhere MySQL user
        'PASSWORD': '@Hoyanga-1998#',      # Replace with MySQL password
        'HOST': 'Reuben1998.mysql.pythonanywhere-services.com',
        'PORT': '3306',
    }
}

# ===================== AUTH =====================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1
LOGIN_REDIRECT_URL = 'dashboard'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

ACCOUNT_FORMS = {
    "signup": "content.forms.CustomSignupForm",
    "login": "content.forms.CustomLoginForm",
}

# ===================== EMAIL (production) =====================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "hoyangareuben@gmail.com"
EMAIL_HOST_PASSWORD = "cqne bljh fccb wrqk"  # App password

# ===================== INTERNATIONALIZATION =====================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

# ===================== STATIC & MEDIA =====================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===================== CKEditor =====================
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            ['bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote'],
            ['imageUpload'],
            ['heading', 'code', 'codeBlock'],
            ['undo', 'redo'],
        ],
        'height': 300,
        'width': '100%',
    }
}

# ===================== SECURITY (production) =====================
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ===================== CRON JOBS =====================
CRONJOBS = [
    ('0 0 * * *', 'membership.tasks.deactivate_expired_members'),
]
