"""
Tests for masking strategies.
"""

import pytest

from django_role_based_masking.exceptions import InvalidStrategyError
from django_role_based_masking.strategies import (
    email,
    full,
    get_strategy,
    noop,
    parse_strategy,
    partial_last,
    percentage,
)


class TestFullStrategy:
    """Tests for the full masking strategy."""

    def test_full_masks_entire_string(self):
        result = full("secret123")
        assert result == "*********"

    def test_full_with_custom_mask_char(self):
        result = full("secret", mask_char="#")
        assert result == "######"

    def test_full_with_empty_string(self):
        result = full("")
        assert result == ""

    def test_full_with_numbers(self):
        result = full("12345")
        assert result == "*****"


class TestPartialLastStrategy:
    """Tests for the partial_last masking strategy."""

    def test_partial_last_default_keep_4(self):
        result = partial_last("1234567890")
        assert result == "******7890"

    def test_partial_last_custom_keep(self):
        result = partial_last("1234567890", keep_last=2)
        assert result == "********90"

    def test_partial_last_shorter_than_keep(self):
        result = partial_last("123", keep_last=4)
        assert result == "123"

    def test_partial_last_exact_length(self):
        result = partial_last("1234", keep_last=4)
        assert result == "1234"

    def test_partial_last_with_custom_mask_char(self):
        result = partial_last("1234567890", keep_last=4, mask_char="#")
        assert result == "######7890"


class TestEmailStrategy:
    """Tests for the email masking strategy."""

    def test_email_masks_local_part(self):
        result = email("john.doe@example.com")
        assert result == "j*******@example.com"

    def test_email_single_char_local(self):
        result = email("j@example.com")
        assert result == "j@example.com"

    def test_email_short_local(self):
        result = email("ab@example.com")
        assert result == "a*@example.com"

    def test_email_invalid_no_at(self):
        result = email("notanemail")
        assert result == "**********"  # full mask of "notanemail" (10 chars)

    def test_email_with_custom_mask_char(self):
        result = email("john@example.com", mask_char="#")
        assert result == "j###@example.com"


class TestPercentageStrategy:
    """Tests for the percentage masking strategy."""

    def test_percentage_default_70(self):
        result = percentage("75000")
        assert result == "****0"  # 70% of 5 = 3.5 -> 4 chars

    def test_percentage_50(self):
        result = percentage("123456", percent=50)
        assert result == "***456"  # 50% of 6 = 3 chars

    def test_percentage_100(self):
        result = percentage("secret", percent=100)
        assert result == "******"

    def test_percentage_0(self):
        result = percentage("secret", percent=0)
        assert result == "secret"

    def test_percentage_with_custom_mask_char(self):
        result = percentage("12345", percent=60, mask_char="#")
        assert result == "###45"  # 60% of 5 = 3 chars


class TestNoopStrategy:
    """Tests for the noop strategy."""

    def test_noop_returns_unchanged(self):
        result = noop("visible")
        assert result == "visible"

    def test_noop_with_numbers(self):
        result = noop("12345")
        assert result == "12345"


class TestGetStrategy:
    """Tests for get_strategy function."""

    def test_get_strategy_full(self):
        strategy = get_strategy("full")
        assert strategy == full

    def test_get_strategy_partial_last(self):
        strategy = get_strategy("partial_last")
        assert strategy == partial_last

    def test_get_strategy_email(self):
        strategy = get_strategy("email")
        assert strategy == email

    def test_get_strategy_percentage(self):
        strategy = get_strategy("percentage")
        assert strategy == percentage

    def test_get_strategy_noop(self):
        strategy = get_strategy("noop")
        assert strategy == noop

    def test_get_strategy_invalid(self):
        with pytest.raises(InvalidStrategyError) as exc_info:
            get_strategy("invalid_strategy")
        assert "Unknown strategy 'invalid_strategy'" in str(exc_info.value)


class TestParseStrategy:
    """Tests for parse_strategy function."""

    def test_parse_simple_string(self):
        func, kwargs = parse_strategy("full")
        assert func == full
        assert kwargs == {}

    def test_parse_partial_last_with_param(self):
        func, kwargs = parse_strategy("partial_last:4")
        assert func == partial_last
        assert kwargs == {"keep_last": 4}

    def test_parse_percentage_with_param(self):
        func, kwargs = parse_strategy("percentage:70")
        assert func == percentage
        assert kwargs == {"percent": 70}

    def test_parse_callable(self):
        def custom_func(value):
            return value.upper()

        func, kwargs = parse_strategy(custom_func)
        assert func == custom_func
        assert kwargs == {}

    def test_parse_dict_with_name(self):
        spec = {"name": "partial_last", "kwargs": {"keep_last": 3}}
        func, kwargs = parse_strategy(spec)
        assert func == partial_last
        assert kwargs == {"keep_last": 3}

    def test_parse_dict_without_kwargs(self):
        spec = {"name": "full"}
        func, kwargs = parse_strategy(spec)
        assert func == full
        assert kwargs == {}

    def test_parse_dict_missing_name(self):
        with pytest.raises(InvalidStrategyError) as exc_info:
            parse_strategy({"kwargs": {}})
        assert "must contain 'name' key" in str(exc_info.value)

    def test_parse_invalid_param_for_partial_last(self):
        with pytest.raises(InvalidStrategyError) as exc_info:
            parse_strategy("partial_last:invalid")
        assert "Invalid parameter for partial_last" in str(exc_info.value)

    def test_parse_invalid_param_for_percentage(self):
        with pytest.raises(InvalidStrategyError) as exc_info:
            parse_strategy("percentage:invalid")
        assert "Invalid parameter for percentage" in str(exc_info.value)

    def test_parse_param_for_unsupported_strategy(self):
        with pytest.raises(InvalidStrategyError) as exc_info:
            parse_strategy("full:param")
        assert "does not support parameters" in str(exc_info.value)

    def test_parse_invalid_type(self):
        with pytest.raises(InvalidStrategyError) as exc_info:
            parse_strategy(123)
        assert "Invalid strategy specification" in str(exc_info.value)
