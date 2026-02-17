"""
Tests for utility functions.
"""

from django_role_based_masking.utils import get_attr, resolve_user_role


class TestGetAttr:
    """Tests for get_attr function."""

    def test_get_simple_attr(self):
        class SimpleObj:
            role = "ADMIN"

        obj = SimpleObj()
        result = get_attr(obj, "role")
        assert result == "ADMIN"

    def test_get_nested_attr(self):
        class Profile:
            role = "MANAGER"

        class User:
            profile = Profile()

        user = User()
        result = get_attr(user, "profile.role")
        assert result == "MANAGER"

    def test_get_deeply_nested_attr(self):
        class Role:
            name = "ADMIN"

        class Profile:
            role = Role()

        class User:
            profile = Profile()

        user = User()
        result = get_attr(user, "profile.role.name")
        assert result == "ADMIN"

    def test_get_missing_attr(self):
        class SimpleObj:
            pass

        obj = SimpleObj()
        result = get_attr(obj, "missing")
        assert result is None

    def test_get_missing_nested_attr(self):
        class Profile:
            pass

        class User:
            profile = Profile()

        user = User()
        result = get_attr(user, "profile.missing")
        assert result is None

    def test_get_attr_with_none_in_path(self):
        class User:
            profile = None

        user = User()
        result = get_attr(user, "profile.role")
        assert result is None

    def test_get_attr_empty_path(self):
        class SimpleObj:
            role = "ADMIN"

        obj = SimpleObj()
        result = get_attr(obj, "")
        assert result is None


class TestResolveUserRole:
    """Tests for resolve_user_role function."""

    def test_resolve_authenticated_user_role(self, regular_user):
        role = resolve_user_role(regular_user)
        assert role == "USER"

    def test_resolve_admin_role(self, admin_user):
        role = resolve_user_role(admin_user)
        assert role == "ADMIN"

    def test_resolve_manager_role(self, manager_user):
        role = resolve_user_role(manager_user)
        assert role == "MANAGER"

    def test_resolve_none_user(self):
        role = resolve_user_role(None)
        assert role == "ANONYMOUS"

    def test_resolve_anonymous_user(self, anonymous_user):
        role = resolve_user_role(anonymous_user)
        assert role == "ANONYMOUS"

    def test_resolve_role_uppercased(self, db):
        from tests.testapp.models import TestUser

        user = TestUser.objects.create(username="lowercase", role="admin")
        role = resolve_user_role(user)
        assert role == "ADMIN"

    def test_resolve_user_without_role(self, db):
        from tests.testapp.models import TestUser

        user = TestUser.objects.create(username="norole")
        user.role = None
        role = resolve_user_role(user)
        assert role == "ANONYMOUS"

    def test_resolve_with_nested_role_attr(self, db):
        """Test with a user that has nested role attribute."""
        from tests.testapp.models import TestUser

        class Profile:
            user_role = "CUSTOM"

        user = TestUser.objects.create(username="nested", role="USER")
        user.profile = Profile()

        # Temporarily change settings
        from django_role_based_masking import settings as drm_settings

        original_attr = drm_settings.ROLE_ATTR
        drm_settings.ROLE_ATTR = "profile.user_role"

        try:
            role = resolve_user_role(user)
            assert role == "CUSTOM"
        finally:
            drm_settings.ROLE_ATTR = original_attr
