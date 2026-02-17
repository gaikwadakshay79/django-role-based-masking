"""
django-role-based-masking

A Django REST Framework package for role-based field masking in serializers.
"""

__version__ = "0.1.0"
__author__ = "django-role-based-masking contributors"
__license__ = "MIT"

from django_role_based_masking.serializers import (
    RoleMaskedModelSerializer,
    RoleMaskedSerializer,
    RoleMaskedSerializerMixin,
)

__all__ = [
    "RoleMaskedModelSerializer",
    "RoleMaskedSerializer",
    "RoleMaskedSerializerMixin",
    "__version__",
]
