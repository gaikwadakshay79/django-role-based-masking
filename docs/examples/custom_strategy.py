"""
Custom masking strategy example for django-role-based-masking.

This example demonstrates how to create and use custom masking strategies
beyond the built-in ones.
"""

import hashlib

from rest_framework import serializers

from django_role_based_masking.serializers import RoleMaskedSerializer
from django_role_based_masking.strategies import STRATEGIES


# Example 1: Simple Custom Strategy
def mask_middle(value, mask_char="*"):
    """
    Custom strategy that masks the middle portion of a string,
    keeping the first and last 25% visible.

    Example:
        "1234567890" -> "12****90"
    """
    value_str = str(value)
    length = len(value_str)

    if length <= 4:
        return value_str

    keep_each_side = max(1, length // 4)
    mask_length = length - (2 * keep_each_side)

    return value_str[:keep_each_side] + mask_char * mask_length + value_str[-keep_each_side:]


# Example 2: Custom Strategy with Parameters
def mask_pattern(value, pattern="****", mask_char="*"):
    """
    Custom strategy that replaces the value with a fixed pattern.

    Args:
        value: The value to mask
        pattern: The pattern to use (default: "****")
        mask_char: Character for additional masking if needed

    Example:
        mask_pattern("secret", pattern="[REDACTED]") -> "[REDACTED]"
    """
    return pattern


# Example 3: Conditional Custom Strategy
def mask_if_long(value, threshold=10, mask_char="*"):
    """
    Custom strategy that only masks if the value is longer than threshold.

    Args:
        value: The value to mask
        threshold: Minimum length to trigger masking
        mask_char: Character to use for masking

    Example:
        mask_if_long("short", threshold=10) -> "short"
        mask_if_long("verylongstring", threshold=10) -> "**************"
    """
    value_str = str(value)
    if len(value_str) > threshold:
        return mask_char * len(value_str)
    return value_str


# Example 4: Format-Preserving Custom Strategy
def mask_credit_card(value, mask_char="*"):
    """
    Custom strategy for credit card numbers that preserves formatting.

    Masks all but the last 4 digits while preserving spaces/dashes.

    Example:
        "1234-5678-9012-3456" -> "****-****-****-3456"
        "1234 5678 9012 3456" -> "**** **** **** 3456"
    """
    value_str = str(value)

    # Extract digits and separators
    digits = []
    separators = []
    separator_positions = []

    for i, char in enumerate(value_str):
        if char.isdigit():
            digits.append(char)
        else:
            separators.append(char)
            separator_positions.append(i)

    # Mask all but last 4 digits
    if len(digits) > 4:
        masked_digits = [mask_char] * (len(digits) - 4) + digits[-4:]
    else:
        masked_digits = digits

    # Reconstruct with separators
    result = []
    digit_index = 0
    for i in range(len(value_str)):
        if i in separator_positions:
            result.append(value_str[i])
        else:
            result.append(masked_digits[digit_index])
            digit_index += 1

    return "".join(result)


# Example 5: Hash-Based Custom Strategy


def mask_with_hash(value, length=8, mask_char="*"):
    """
    Custom strategy that replaces value with a hash prefix.

    Useful for debugging while maintaining privacy.

    Example:
        mask_with_hash("secret123") -> "a1b2c3d4"
    """
    hash_obj = hashlib.sha256(str(value).encode())
    hash_hex = hash_obj.hexdigest()
    return hash_hex[:length]


# Using Custom Strategies in Serializers


class PaymentSerializer(RoleMaskedSerializer):
    """
    Example serializer using custom masking strategies.
    """

    cardholder_name = serializers.CharField()
    card_number = serializers.CharField()
    cvv = serializers.CharField()
    account_number = serializers.CharField()

    mask_fields = {
        "ADMIN": {},
        "SUPPORT": {
            # Use custom callable directly
            "card_number": mask_credit_card,
            "cvv": mask_pattern,
            "account_number": mask_middle,
        },
        "CUSTOMER": {
            # Use custom callable with parameters via dict
            "card_number": mask_credit_card,
            "cvv": {
                "name": "full",  # Can also use built-in strategies
                "kwargs": {},
            },
            "account_number": mask_middle,
        },
        "GUEST": {
            "cardholder_name": mask_middle,
            "card_number": lambda v: "****-****-****-****",  # Lambda function
            "cvv": "full",
            "account_number": "full",
        },
    }


# Example with Parameterized Custom Strategy
class SecureDataSerializer(RoleMaskedSerializer):
    """
    Example using custom strategies with parameters.
    """

    api_key = serializers.CharField()
    secret_token = serializers.CharField()
    internal_id = serializers.CharField()

    mask_fields = {
        "ADMIN": {},
        "DEVELOPER": {
            # Pass custom function with parameters
            "api_key": lambda v: mask_if_long(v, threshold=20),
            "secret_token": mask_with_hash,
            "internal_id": mask_middle,
        },
        "USER": {
            "api_key": "full",
            "secret_token": "full",
            "internal_id": "full",
        },
    }


# Example Output
"""
Original Data:
{
    "cardholder_name": "John Doe",
    "card_number": "1234-5678-9012-3456",
    "cvv": "123",
    "account_number": "9876543210"
}

SUPPORT sees (with custom strategies):
{
    "cardholder_name": "John Doe",
    "card_number": "****-****-****-3456",
    "cvv": "****",
    "account_number": "98****10"
}

CUSTOMER sees:
{
    "cardholder_name": "John Doe",
    "card_number": "****-****-****-3456",
    "cvv": "***",
    "account_number": "98****10"
}

GUEST sees:
{
    "cardholder_name": "Jo****oe",
    "card_number": "****-****-****-****",
    "cvv": "***",
    "account_number": "**********"
}
"""


# Advanced: Registering Custom Strategies Globally


def register_custom_strategy(name, func):
    """
    Register a custom strategy globally so it can be used by name.

    Usage:
        register_custom_strategy("credit_card", mask_credit_card)

        # Then use in serializer:
        mask_fields = {
            "USER": {
                "card_number": "credit_card"
            }
        }
    """
    STRATEGIES[name] = func


# Register custom strategies
register_custom_strategy("credit_card", mask_credit_card)
register_custom_strategy("middle", mask_middle)
register_custom_strategy("hash", mask_with_hash)


class GlobalCustomStrategySerializer(RoleMaskedSerializer):
    """
    Example using globally registered custom strategies.
    """

    card_number = serializers.CharField()
    secret = serializers.CharField()

    mask_fields = {
        "USER": {
            "card_number": "credit_card",  # Use registered strategy by name
            "secret": "hash",
        }
    }
