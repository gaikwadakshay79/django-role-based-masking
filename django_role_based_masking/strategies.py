"""
Built-in masking strategies for django-role-based-masking.
"""

import math

from django_role_based_masking import settings as drm_settings
from django_role_based_masking.exceptions import InvalidStrategyError


def full(value, mask_char=None):
    """
    Mask the entire string.

    Args:
        value: The value to mask
        mask_char: Character to use for masking (default from settings)

    Returns:
        Fully masked string

    Example:
        >>> full("secret123")
        "*********"
    """
    if mask_char is None:
        mask_char = drm_settings.MASK_CHAR
    return mask_char * len(str(value))


def partial_last(value, keep_last=4, mask_char=None):
    """
    Keep the last N characters, mask the rest.

    Args:
        value: The value to mask
        keep_last: Number of characters to keep at the end
        mask_char: Character to use for masking (default from settings)

    Returns:
        Partially masked string with last N characters visible

    Example:
        >>> partial_last("1234567890", keep_last=4)
        "******7890"
    """
    if mask_char is None:
        mask_char = drm_settings.MASK_CHAR

    value_str = str(value)
    if len(value_str) <= keep_last:
        return value_str

    mask_length = len(value_str) - keep_last
    return mask_char * mask_length + value_str[-keep_last:]


def email(value, mask_char=None):
    """
    Mask email local-part except the first character.

    Args:
        value: The email address to mask
        mask_char: Character to use for masking (default from settings)

    Returns:
        Masked email with first character and domain visible

    Example:
        >>> email("john.doe@example.com")
        "j*******@example.com"
    """
    if mask_char is None:
        mask_char = drm_settings.MASK_CHAR

    value_str = str(value)
    if "@" not in value_str:
        # Not a valid email, mask entire string
        return full(value_str, mask_char)

    local_part, domain = value_str.rsplit("@", 1)
    if len(local_part) <= 1:
        return value_str

    masked_local = local_part[0] + mask_char * (len(local_part) - 1)
    return f"{masked_local}@{domain}"


def percentage(value, percent=70, mask_char=None):
    """
    Mask a percentage of the string length from the left.

    Args:
        value: The value to mask
        percent: Percentage of string to mask (0-100)
        mask_char: Character to use for masking (default from settings)

    Returns:
        String with specified percentage masked from left

    Example:
        >>> percentage("75000", percent=70)
        "****0"  # 70% of 5 chars = 3.5 -> 4 chars masked
    """
    if mask_char is None:
        mask_char = drm_settings.MASK_CHAR

    value_str = str(value)
    if percent <= 0:
        return value_str
    if percent >= 100:
        return full(value_str, mask_char)

    mask_length = math.ceil(len(value_str) * percent / 100)
    return mask_char * mask_length + value_str[mask_length:]


def noop(value):
    """
    No masking - return value unchanged.

    Args:
        value: The value to return

    Returns:
        Original value unchanged

    Example:
        >>> noop("visible")
        "visible"
    """
    return value


# Strategy registry
STRATEGIES = {
    "full": full,
    "partial_last": partial_last,
    "email": email,
    "percentage": percentage,
    "noop": noop,
}


def get_strategy(name):
    """
    Get a strategy function by name.

    Args:
        name: Strategy name

    Returns:
        Strategy function

    Raises:
        InvalidStrategyError: If strategy name is not found
    """
    if name not in STRATEGIES:
        raise InvalidStrategyError(
            f"Unknown strategy '{name}'. Available strategies: {', '.join(STRATEGIES.keys())}"
        )
    return STRATEGIES[name]


def parse_strategy(spec):
    """
    Parse a strategy specification into a callable and kwargs.

    Args:
        spec: Strategy specification, can be:
            - str: "full", "partial_last:4", "percentage:70"
            - callable: custom function
            - dict: {"name": "partial_last", "kwargs": {"keep_last": 3}}

    Returns:
        Tuple of (callable, kwargs_dict)

    Raises:
        InvalidStrategyError: If spec format is invalid

    Examples:
        >>> parse_strategy("full")
        (<function full>, {})

        >>> parse_strategy("partial_last:4")
        (<function partial_last>, {"keep_last": 4})

        >>> parse_strategy({"name": "percentage", "kwargs": {"percent": 80}})
        (<function percentage>, {"percent": 80})
    """
    # If it's already a callable, return it with empty kwargs
    if callable(spec):
        return spec, {}

    # If it's a dict with name and kwargs
    if isinstance(spec, dict):
        if "name" not in spec:
            raise InvalidStrategyError("Strategy dict must contain 'name' key")

        strategy_name = spec["name"]
        strategy_kwargs = spec.get("kwargs", {})

        strategy_func = get_strategy(strategy_name)
        return strategy_func, strategy_kwargs

    # If it's a string, parse it
    if isinstance(spec, str):
        # Check for parameterized strategy like "partial_last:4"
        if ":" in spec:
            parts = spec.split(":", 1)
            strategy_name = parts[0]
            param_value = parts[1]

            strategy_func = get_strategy(strategy_name)

            # Determine the parameter name based on strategy
            if strategy_name == "partial_last":
                try:
                    return strategy_func, {"keep_last": int(param_value)}
                except ValueError:
                    raise InvalidStrategyError(
                        f"Invalid parameter for partial_last: '{param_value}' (expected integer)"
                    ) from None
            elif strategy_name == "percentage":
                try:
                    return strategy_func, {"percent": int(param_value)}
                except ValueError:
                    raise InvalidStrategyError(
                        f"Invalid parameter for percentage: '{param_value}' (expected integer)"
                    ) from None
            else:
                raise InvalidStrategyError(
                    f"Strategy '{strategy_name}' does not support parameters"
                )
        else:
            # Simple strategy name without parameters
            strategy_func = get_strategy(spec)
            return strategy_func, {}

    raise InvalidStrategyError(
        f"Invalid strategy specification: {spec}. "
        "Expected string, callable, or dict with 'name' key."
    )
