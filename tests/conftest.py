"""
Pytest configuration and fixtures for django-role-based-masking tests.
"""

import pytest
from django.conf import settings


def pytest_configure(config):
    """Configure Django settings for pytest."""
    if not settings.configured:
        settings.configure(
            SECRET_KEY="test-secret-key",
            DEBUG=True,
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "rest_framework",
                "django_role_based_masking",
                "tests.testapp",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            AUTH_USER_MODEL="testapp.TestUser",
            DRM_ROLE_ATTR="role",
            DRM_MASK_CHAR="*",
            DRM_DEFAULT_STRATEGY="full",
            USE_TZ=True,
            ROOT_URLCONF=[],
            MIDDLEWARE=[],
        )

    # Setup Django
    import django

    if not django.apps.apps.ready:
        django.setup()


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    from tests.testapp.models import TestUser

    return TestUser.objects.create(username="admin", role="ADMIN")


@pytest.fixture
def manager_user(db):
    """Create a manager user for testing."""
    from tests.testapp.models import TestUser

    return TestUser.objects.create(username="manager", role="MANAGER")


@pytest.fixture
def regular_user(db):
    """Create a regular user for testing."""
    from tests.testapp.models import TestUser

    return TestUser.objects.create(username="user", role="USER")


@pytest.fixture
def anonymous_user():
    """Create an anonymous user for testing."""
    from django.contrib.auth.models import AnonymousUser

    return AnonymousUser()


@pytest.fixture
def mock_request_factory():
    """Factory for creating mock DRF requests."""
    from rest_framework.test import APIRequestFactory

    return APIRequestFactory()


@pytest.fixture
def mock_request(mock_request_factory, regular_user):
    """Create a mock request with a regular user."""
    request = mock_request_factory.get("/")
    request.user = regular_user
    return request


@pytest.fixture
def employee_data():
    """Sample employee data for testing."""
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "salary": "75000",
        "ssn": "123-45-6789",
        "pan": "ABCDE1234F",
    }


@pytest.fixture
def nested_employee_data():
    """Sample nested employee data for testing."""
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "profile": {
            "phone": "+1234567890",
            "pan": "ABCDE1234F",
        },
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "postal_code": "10001",
        },
    }
