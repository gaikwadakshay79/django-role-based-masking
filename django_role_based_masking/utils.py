"""
Utility functions for django-role-based-masking.
"""

from django_role_based_masking import settings as drm_settings


def get_attr(obj, path):
    """
    Get an attribute from an object using dotted path notation.

    Args:
        obj: The object to get the attribute from
        path: Dotted path string (e.g., "profile.role")

    Returns:
        The attribute value or None if not found

    Examples:
        >>> user = User(profile=Profile(role="ADMIN"))
        >>> get_attr(user, "profile.role")
        "ADMIN"

        >>> get_attr(user, "role")
        None
    """
    if not path:
        return None

    parts = path.split(".")
    current = obj

    for part in parts:
        try:
            current = getattr(current, part, None)
            if current is None:
                return None
        except (AttributeError, TypeError):
            return None

    return current


def resolve_user_role(user):
    """
    Resolve the role of a user based on configured role attribute path.

    Args:
        user: Django user object or None

    Returns:
        Role string (uppercased) or "ANONYMOUS" if user is not authenticated

    Examples:
        >>> resolve_user_role(authenticated_user)
        "ADMIN"

        >>> resolve_user_role(None)
        "ANONYMOUS"

        >>> resolve_user_role(anonymous_user)
        "ANONYMOUS"
    """
    # Handle None or anonymous users
    if user is None or not user.is_authenticated:
        return "ANONYMOUS"

    # Get role using configured attribute path
    role = get_attr(user, drm_settings.ROLE_ATTR)

    # If role not found, return ANONYMOUS
    if role is None:
        return "ANONYMOUS"

    # Return uppercased role
    return str(role).upper()
