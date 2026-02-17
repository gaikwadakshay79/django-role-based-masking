"""
Configuration settings for django-role-based-masking.
"""

from django.conf import settings


def get_setting(name, default):
    """
    Get a setting value from Django settings with a fallback default.

    Args:
        name: Setting name (without DRM_ prefix)
        default: Default value if setting is not found

    Returns:
        The setting value or default
    """
    return getattr(settings, f"DRM_{name}", default)


# Default role attribute path (supports dotted paths like "profile.role")
ROLE_ATTR = get_setting("ROLE_ATTR", "role")

# Default masking character
MASK_CHAR = get_setting("MASK_CHAR", "*")

# Default strategy when not specified
DEFAULT_STRATEGY = get_setting("DEFAULT_STRATEGY", "full")
