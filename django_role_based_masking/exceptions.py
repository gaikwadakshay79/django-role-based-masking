"""
Custom exceptions for django-role-based-masking.
"""


class MaskingError(Exception):
    """Base exception for masking-related errors."""

    pass


class InvalidStrategyError(MaskingError):
    """Raised when an invalid masking strategy is specified."""

    pass


class InvalidRoleError(MaskingError):
    """Raised when an invalid role is encountered."""

    pass


class ConfigurationError(MaskingError):
    """Raised when there's a configuration error."""

    pass
