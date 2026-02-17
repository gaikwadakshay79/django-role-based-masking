"""
Test serializers for django-role-based-masking tests.
"""

from rest_framework import serializers

from django_role_based_masking.serializers import RoleMaskedModelSerializer, RoleMaskedSerializer
from tests.testapp.models import EmployeeProfile


class EmployeeProfileSerializer(RoleMaskedModelSerializer):
    """Serializer for EmployeeProfile with role-based masking."""

    class Meta:
        model = EmployeeProfile
        fields = ["id", "name", "email", "phone", "salary", "ssn", "pan"]

        mask_fields = {
            "ADMIN": {},  # No masking for admins
            "MANAGER": {
                "ssn": "partial_last:4",
                "salary": "percentage:50",
            },
            "USER": {
                "email": "email",
                "phone": "partial_last:4",
                "salary": "full",
                "ssn": "full",
                "pan": "partial_last:4",
            },
            "ANONYMOUS": {
                "email": "full",
                "phone": "full",
                "salary": "full",
                "ssn": "full",
                "pan": "full",
            },
        }


class SimpleDataSerializer(RoleMaskedSerializer):
    """Simple serializer for testing with non-model data."""

    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()

    mask_fields = {
        "GUEST": {
            "email": "email",
            "phone": "partial_last:4",
        }
    }


class NestedAddressSerializer(serializers.Serializer):
    """Nested serializer for address data."""

    street = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()


class NestedProfileSerializer(serializers.Serializer):
    """Nested serializer for profile data."""

    phone = serializers.CharField()
    pan = serializers.CharField()


class NestedEmployeeSerializer(RoleMaskedSerializer):
    """Serializer with nested data for testing nested masking."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    profile = NestedProfileSerializer()
    address = NestedAddressSerializer()

    mask_fields = {
        "ADMIN": {},
        "USER": {
            "email": "email",
            "profile.phone": "partial_last:4",
            "profile.pan": "partial_last:4",
            "address.street": "full",
            "address.postal_code": "partial_last:3",
        },
        "GUEST": {
            "email": "full",
            "profile.phone": "full",
            "profile.pan": "full",
            "address.street": "full",
            "address.city": "full",
            "address.postal_code": "full",
        },
    }


class DefaultRoleSerializer(RoleMaskedSerializer):
    """Serializer with DEFAULT role fallback."""

    name = serializers.CharField()
    secret = serializers.CharField()

    mask_fields = {
        "ADMIN": {},
        "DEFAULT": {
            "secret": "full",
        },
    }
