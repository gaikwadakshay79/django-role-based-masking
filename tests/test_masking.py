"""
Tests for the core masking engine.
"""

from django_role_based_masking.masking import (
    apply_field_masking,
    apply_masking,
    apply_nested_masking,
)


class TestApplyFieldMasking:
    """Tests for apply_field_masking function."""

    def test_apply_full_strategy(self):
        result = apply_field_masking("secret", "full")
        assert result == "******"

    def test_apply_partial_last_strategy(self):
        result = apply_field_masking("1234567890", "partial_last:4")
        assert result == "******7890"

    def test_apply_email_strategy(self):
        result = apply_field_masking("john@example.com", "email")
        assert result == "j***@example.com"

    def test_apply_percentage_strategy(self):
        result = apply_field_masking("12345", "percentage:60")
        assert result == "***45"

    def test_apply_with_none_value(self):
        result = apply_field_masking(None, "full")
        assert result is None

    def test_apply_with_callable(self):
        def custom_mask(value):
            return "MASKED"

        result = apply_field_masking("secret", custom_mask)
        assert result == "MASKED"


class TestApplyNestedMasking:
    """Tests for apply_nested_masking function."""

    def test_mask_nested_dict_field(self):
        data = {"name": "John", "profile": {"phone": "1234567890"}}
        result = apply_nested_masking(data, "profile.phone", "partial_last:4")
        assert result["profile"]["phone"] == "******7890"
        assert result["name"] == "John"

    def test_mask_deeply_nested_field(self):
        data = {"user": {"profile": {"contact": {"phone": "1234567890"}}}}
        result = apply_nested_masking(data, "user.profile.contact.phone", "full")
        assert result["user"]["profile"]["contact"]["phone"] == "**********"

    def test_mask_missing_nested_field(self):
        data = {"name": "John"}
        result = apply_nested_masking(data, "profile.phone", "full")
        assert result == {"name": "John"}

    def test_mask_nested_field_in_list(self):
        data = {"items": [{"name": "Item1", "price": "100"}, {"name": "Item2", "price": "200"}]}
        result = apply_nested_masking(data, "items.price", "full")
        # Should mask price in all list items
        assert result["items"][0]["price"] == "***"
        assert result["items"][1]["price"] == "***"


class TestApplyMasking:
    """Tests for apply_masking function."""

    def test_admin_sees_unmasked(self, mock_request_factory, admin_user):
        request = mock_request_factory.get("/")
        request.user = admin_user

        data = {"name": "John Doe", "email": "john@example.com", "salary": "75000"}

        rules = {"ADMIN": {}, "USER": {"email": "email", "salary": "full"}}

        result = apply_masking(data, rules, {"request": request})
        assert result["email"] == "john@example.com"
        assert result["salary"] == "75000"

    def test_user_sees_masked_fields(self, mock_request_factory, regular_user):
        request = mock_request_factory.get("/")
        request.user = regular_user

        data = {"name": "John Doe", "email": "john@example.com", "salary": "75000"}

        rules = {"ADMIN": {}, "USER": {"email": "email", "salary": "full"}}

        result = apply_masking(data, rules, {"request": request})
        assert result["name"] == "John Doe"
        assert result["email"] == "j***@example.com"
        assert result["salary"] == "*****"

    def test_anonymous_uses_anonymous_rules(self, mock_request_factory, anonymous_user):
        request = mock_request_factory.get("/")
        request.user = anonymous_user

        data = {"name": "John Doe", "email": "john@example.com", "phone": "1234567890"}

        rules = {"USER": {"email": "email"}, "ANONYMOUS": {"email": "full", "phone": "full"}}

        result = apply_masking(data, rules, {"request": request})
        assert result["name"] == "John Doe"
        # full mask of "john@example.com" (16 chars)
        assert result["email"] == "****************"
        assert result["phone"] == "**********"

    def test_unknown_role_falls_back_to_default(self, mock_request_factory, db):
        from tests.testapp.models import TestUser

        unknown_user = TestUser.objects.create(username="unknown", role="UNKNOWN")
        request = mock_request_factory.get("/")
        request.user = unknown_user

        data = {"name": "John Doe", "secret": "confidential"}

        rules = {"ADMIN": {}, "DEFAULT": {"secret": "full"}}

        result = apply_masking(data, rules, {"request": request})
        assert result["name"] == "John Doe"
        assert result["secret"] == "************"

    def test_no_matching_rules_returns_unchanged(self, mock_request_factory, regular_user):
        request = mock_request_factory.get("/")
        request.user = regular_user

        data = {"name": "John Doe", "email": "john@example.com"}

        rules = {"ADMIN": {}, "MANAGER": {"email": "email"}}

        result = apply_masking(data, rules, {"request": request})
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"

    def test_no_rules_returns_unchanged(self, mock_request_factory, regular_user):
        request = mock_request_factory.get("/")
        request.user = regular_user

        data = {"name": "John Doe"}
        result = apply_masking(data, {}, {"request": request})
        assert result == {"name": "John Doe"}

    def test_no_request_returns_unchanged(self, regular_user):
        data = {"name": "John Doe", "email": "john@example.com"}
        rules = {"USER": {"email": "email"}}

        result = apply_masking(data, rules, {})
        assert result == data

    def test_dotted_nested_masking(self, mock_request_factory, regular_user):
        request = mock_request_factory.get("/")
        request.user = regular_user

        data = {"name": "John Doe", "profile": {"phone": "1234567890", "pan": "ABCDE1234F"}}

        rules = {"USER": {"profile.phone": "partial_last:4", "profile.pan": "partial_last:4"}}

        result = apply_masking(data, rules, {"request": request})
        assert result["name"] == "John Doe"
        assert result["profile"]["phone"] == "******7890"
        assert result["profile"]["pan"] == "******234F"

    def test_mixed_top_level_and_nested_masking(self, mock_request_factory, regular_user):
        request = mock_request_factory.get("/")
        request.user = regular_user

        data = {
            "email": "john@example.com",
            "address": {"street": "123 Main St", "city": "New York"},
        }

        rules = {"USER": {"email": "email", "address.street": "full"}}

        result = apply_masking(data, rules, {"request": request})
        assert result["email"] == "j***@example.com"
        assert result["address"]["street"] == "***********"
        assert result["address"]["city"] == "New York"

    def test_empty_role_rules_returns_unchanged(self, mock_request_factory, admin_user):
        request = mock_request_factory.get("/")
        request.user = admin_user

        data = {"name": "John", "email": "john@example.com"}
        rules = {"ADMIN": {}}

        result = apply_masking(data, rules, {"request": request})
        assert result == data
