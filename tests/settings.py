"""
Django settings for tests.
"""

SECRET_KEY = "test-secret-key-for-django-role-based-masking"

DEBUG = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "django_role_based_masking",
    "tests.testapp",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

AUTH_USER_MODEL = "testapp.TestUser"

# django-role-based-masking settings
DRM_ROLE_ATTR = "role"
DRM_MASK_CHAR = "*"
DRM_DEFAULT_STRATEGY = "full"

USE_TZ = True

ROOT_URLCONF = []

MIDDLEWARE = []
