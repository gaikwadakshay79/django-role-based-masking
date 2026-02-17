"""
Core masking engine for django-role-based-masking.
"""

from django_role_based_masking.strategies import parse_strategy
from django_role_based_masking.utils import resolve_user_role


def apply_field_masking(value, strategy_spec):
    """
    Apply a masking strategy to a single value.

    Args:
        value: The value to mask
        strategy_spec: Strategy specification (string, callable, or dict)

    Returns:
        Masked value
    """
    if value is None:
        return None

    strategy_func, strategy_kwargs = parse_strategy(strategy_spec)
    return strategy_func(value, **strategy_kwargs)


def apply_nested_masking(data, field_path, strategy_spec):
    """
    Apply masking to a nested field using dotted path notation.

    Args:
        data: The data dictionary
        field_path: Dotted path to the field (e.g., "address.city")
        strategy_spec: Strategy specification

    Returns:
        Modified data dictionary
    """
    parts = field_path.split(".")

    # Navigate to the parent of the target field
    current = data
    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            return data
        current = current[part]

        # Handle lists - apply to each dict element
        if isinstance(current, list):
            for item in current:
                if isinstance(item, dict):
                    remaining_path = ".".join(parts[parts.index(part) + 1 :])
                    apply_nested_masking(item, remaining_path, strategy_spec)
            return data

    # Apply masking to the target field
    target_field = parts[-1]
    if isinstance(current, dict) and target_field in current:
        current[target_field] = apply_field_masking(current[target_field], strategy_spec)

    return data


def apply_masking(data, rules, context):
    """
    Apply role-based masking to serializer output data.

    Args:
        data: Serializer output dictionary
        rules: Role-based masking rules dictionary
        context: Serializer context (must contain 'request')

    Returns:
        Modified data dictionary with masked fields

    Example:
        >>> rules = {
        ...     "ADMIN": {},
        ...     "USER": {
        ...         "email": "email",
        ...         "phone": "partial_last:4"
        ...     }
        ... }
        >>> data = {"name": "John", "email": "john@example.com", "phone": "1234567890"}
        >>> apply_masking(data, rules, {"request": request})
        {"name": "John", "email": "j***@example.com", "phone": "******7890"}
    """
    # If no rules provided, return data unchanged
    if not rules:
        return data

    # Get request from context
    request = context.get("request")
    if not request:
        return data

    # Resolve user role
    user = getattr(request, "user", None)
    role = resolve_user_role(user)

    # Determine which rules to apply (priority order)
    role_rules = None

    # 1. Try exact role match
    if role in rules:
        role_rules = rules[role]
    # 2. Try DEFAULT role
    elif "DEFAULT" in rules:
        role_rules = rules["DEFAULT"]
    # 3. Try ANONYMOUS role (if user is anonymous)
    elif role == "ANONYMOUS" and "ANONYMOUS" in rules:
        role_rules = rules["ANONYMOUS"]

    # If no matching rules, return data unchanged
    if role_rules is None:
        return data

    # If rules are empty dict, no masking needed
    if not role_rules:
        return data

    # Make a copy of data to avoid modifying the original
    masked_data = data.copy() if isinstance(data, dict) else data

    # Apply masking for each field in the rules
    for field_path, strategy_spec in role_rules.items():
        if "." in field_path:
            # Handle nested field with dotted path
            masked_data = apply_nested_masking(masked_data, field_path, strategy_spec)
        else:
            # Handle top-level field
            if field_path in masked_data:
                masked_data[field_path] = apply_field_masking(
                    masked_data[field_path], strategy_spec
                )

    return masked_data
