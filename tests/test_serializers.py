"""
Tests for DRF serializer integration.
"""

import pytest

from tests.testapp.serializers import (
    DefaultRoleSerializer,
    EmployeeProfileSerializer,
    NestedEmployeeSerializer,
    SimpleDataSerializer,
)


class TestRoleMaskedModelSerializer:
    """Tests for RoleMaskedModelSerializer."""

    @pytest.fixture
    def employee_instance(self, db):
        from tests.testapp.models import EmployeeProfile

        return EmployeeProfile.objects.create(
            name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            salary="75000",
            ssn="123-45-6789",
            pan="ABCDE1234F",
        )

    def test_admin_sees_unmasked_data(self, employee_instance, mock_request_factory, admin_user):
        request = mock_request_factory.get("/")
        request.user = admin_user

        serializer = EmployeeProfileSerializer(employee_instance, context={"request": request})

        data = serializer.data
        assert data["email"] == "john.doe@example.com"
        assert data["phone"] == "+1234567890"
        assert data["salary"] == "75000"
        assert data["ssn"] == "123-45-6789"
        assert data["pan"] == "ABCDE1234F"

    def test_manager_sees_partially_masked_data(
        self, employee_instance, mock_request_factory, manager_user
    ):
        request = mock_request_factory.get("/")
        request.user = manager_user

        serializer = EmployeeProfileSerializer(employee_instance, context={"request": request})

        data = serializer.data
        # Not masked for manager
        assert data["email"] == "john.doe@example.com"
        assert data["phone"] == "+1234567890"  # Not masked for manager
        # 50% masked (50% of 5 = 2.5 -> 3 chars masked)
        assert data["salary"] == "***00"
        assert data["ssn"] == "*******6789"  # Last 4 visible
        assert data["pan"] == "ABCDE1234F"  # Not masked for manager

    def test_user_sees_masked_data(self, employee_instance, mock_request_factory, regular_user):
        request = mock_request_factory.get("/")
        request.user = regular_user

        serializer = EmployeeProfileSerializer(employee_instance, context={"request": request})

        data = serializer.data
        assert data["name"] == "John Doe"
        assert data["email"] == "j*******@example.com"
        # partial_last:4 on "+1234567890" (11 chars)
        assert data["phone"] == "*******7890"
        assert data["salary"] == "*****"
        assert data["ssn"] == "***********"
        assert data["pan"] == "******234F"

    def test_anonymous_sees_fully_masked_data(
        self, employee_instance, mock_request_factory, anonymous_user
    ):
        request = mock_request_factory.get("/")
        request.user = anonymous_user

        serializer = EmployeeProfileSerializer(employee_instance, context={"request": request})

        data = serializer.data
        assert data["name"] == "John Doe"
        # full mask of "john.doe@example.com" (20 chars)
        assert data["email"] == "********************"
        # full mask of "+1234567890" (11 chars)
        assert data["phone"] == "***********"
        assert data["salary"] == "*****"
        assert data["ssn"] == "***********"
        assert data["pan"] == "**********"

    def test_without_request_context_returns_unmasked(self, employee_instance):
        serializer = EmployeeProfileSerializer(employee_instance)
        data = serializer.data

        # Without request context, no masking should occur
        assert data["email"] == "john.doe@example.com"
        assert data["salary"] == "75000"


class TestRoleMaskedSerializer:
    """Tests for RoleMaskedSerializer."""

    def test_simple_serializer_with_masking(self, mock_request_factory, db):
        from tests.testapp.models import TestUser

        guest_user = TestUser.objects.create(username="guest", role="GUEST")
        request = mock_request_factory.get("/")
        request.user = guest_user

        data = {"name": "John Doe", "email": "john@example.com", "phone": "1234567890"}

        serializer = SimpleDataSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        output = serializer.data

        assert output["name"] == "John Doe"
        assert output["email"] == "j***@example.com"
        assert output["phone"] == "******7890"


class TestNestedSerializerMasking:
    """Tests for nested serializer masking."""

    def test_nested_field_masking_for_user(
        self, mock_request_factory, regular_user, nested_employee_data
    ):
        request = mock_request_factory.get("/")
        request.user = regular_user

        serializer = NestedEmployeeSerializer(
            data=nested_employee_data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        output = serializer.data

        assert output["name"] == "John Doe"
        assert output["email"] == "j*******@example.com"
        # partial_last:4 on "+1234567890" (11 chars)
        assert output["profile"]["phone"] == "*******7890"
        assert output["profile"]["pan"] == "******234F"
        assert output["address"]["street"] == "***********"
        assert output["address"]["city"] == "New York"  # Not masked
        assert output["address"]["postal_code"] == "**001"

    def test_nested_field_masking_for_guest(self, mock_request_factory, db, nested_employee_data):
        from tests.testapp.models import TestUser

        guest_user = TestUser.objects.create(username="guest", role="GUEST")
        request = mock_request_factory.get("/")
        request.user = guest_user

        serializer = NestedEmployeeSerializer(
            data=nested_employee_data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        output = serializer.data

        # full mask of "john.doe@example.com" (20 chars)
        assert output["email"] == "********************"
        # full mask of "+1234567890" (11 chars)
        assert output["profile"]["phone"] == "***********"
        assert output["profile"]["pan"] == "**********"
        assert output["address"]["street"] == "***********"
        assert output["address"]["city"] == "********"
        assert output["address"]["postal_code"] == "*****"

    def test_nested_field_masking_for_admin(
        self, mock_request_factory, admin_user, nested_employee_data
    ):
        request = mock_request_factory.get("/")
        request.user = admin_user

        serializer = NestedEmployeeSerializer(
            data=nested_employee_data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        output = serializer.data

        # Admin should see everything unmasked
        assert output["email"] == "john.doe@example.com"
        assert output["profile"]["phone"] == "+1234567890"
        assert output["profile"]["pan"] == "ABCDE1234F"
        assert output["address"]["street"] == "123 Main St"
        assert output["address"]["city"] == "New York"
        assert output["address"]["postal_code"] == "10001"


class TestDefaultRoleFallback:
    """Tests for DEFAULT role fallback behavior."""

    def test_unknown_role_uses_default(self, mock_request_factory, db):
        from tests.testapp.models import TestUser

        unknown_user = TestUser.objects.create(username="unknown", role="UNKNOWN_ROLE")
        request = mock_request_factory.get("/")
        request.user = unknown_user

        data = {"name": "John Doe", "secret": "confidential"}

        serializer = DefaultRoleSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        output = serializer.data

        assert output["name"] == "John Doe"
        assert output["secret"] == "************"

    def test_admin_bypasses_default(self, mock_request_factory, admin_user):
        request = mock_request_factory.get("/")
        request.user = admin_user

        data = {"name": "John Doe", "secret": "confidential"}

        serializer = DefaultRoleSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        output = serializer.data

        assert output["name"] == "John Doe"
        assert output["secret"] == "confidential"


class TestSerializerWithoutMaskFields:
    """Tests for serializers without mask_fields configuration."""

    def test_serializer_without_mask_fields_returns_unmasked(
        self, mock_request_factory, regular_user
    ):
        from rest_framework import serializers

        from django_role_based_masking.serializers import RoleMaskedSerializer

        class NoMaskSerializer(RoleMaskedSerializer):
            name = serializers.CharField()
            email = serializers.EmailField()

        request = mock_request_factory.get("/")
        request.user = regular_user

        data = {"name": "John", "email": "john@example.com"}
        serializer = NoMaskSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        output = serializer.data

        # Without mask_fields, data should be unmasked
        assert output["email"] == "john@example.com"
