# django-role-based-masking

[![PyPI version](https://badge.fury.io/py/django-role-based-masking.svg)](https://badge.fury.io/py/django-role-based-masking)
[![Python versions](https://img.shields.io/pypi/pyversions/django-role-based-masking.svg)](https://pypi.org/project/django-role-based-masking/)
[![Django versions](https://img.shields.io/pypi/djversions/django-role-based-masking.svg)](https://pypi.org/project/django-role-based-masking/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Django REST Framework package that masks serializer output fields based on the requesting user's role using configurable masking strategies.

## Features

- 🎭 **Role-based field masking** - Automatically mask sensitive fields based on user roles
- 🔧 **Flexible strategies** - Built-in masking strategies (full, partial, email, percentage)
- 🪆 **Nested support** - Mask fields in nested serializers using dotted paths
- 🎨 **Custom strategies** - Easy to add custom masking logic
- ⚡ **DRF integration** - Simple mixin for existing serializers
- 🧪 **Well tested** - Comprehensive test suite
- 📦 **Production ready** - Supports Python 3.10+, Django 3.2+, DRF 3.14+

## Installation

```bash
pip install django-role-based-masking
```

## Quick Start

### 1. Basic Usage

```python
from rest_framework import serializers
from django_role_based_masking.serializers import RoleMaskedModelSerializer

class EmployeeSerializer(RoleMaskedModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'phone', 'salary', 'ssn']

        # Define masking rules per role
        mask_fields = {
            "ADMIN": {},  # No masking for admins
            "MANAGER": {
                "ssn": "partial_last:4",
                "salary": "percentage:50",
            },
            "EMPLOYEE": {
                "email": "email",
                "phone": "partial_last:4",
                "salary": "full",
                "ssn": "full",
            },
            "ANONYMOUS": {
                "email": "full",
                "phone": "full",
                "salary": "full",
                "ssn": "full",
            }
        }
```

### 2. Example Output

For a user with role `MANAGER`:

```python
# Original data
{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "salary": "75000",
    "ssn": "123-45-6789"
}

# Masked output
{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "salary": "*****0",  # 50% masked
    "ssn": "***-**-6789"  # Only last 4 visible
}
```

## Built-in Masking Strategies

### `full`

Masks the entire string.

```python
"salary": "full"
# "75000" -> "*****"
```

### `partial_last:N`

Keeps the last N characters, masks the rest.

```python
"ssn": "partial_last:4"
# "123-45-6789" -> "***-**-6789"

"phone": "partial_last:4"
# "+1234567890" -> "*******7890"
```

### `email`

Masks the email local-part except the first character.

```python
"email": "email"
# "john.doe@example.com" -> "j*******@example.com"
```

### `percentage:N`

Masks N% of the string length from the left.

```python
"salary": "percentage:70"
# "75000" -> "****0"  # 70% of 5 chars = 3.5 -> 4 chars masked
```

### `noop`

No masking (passthrough).

```python
"name": "noop"
# "John Doe" -> "John Doe"
```

## Nested Field Masking

Use dotted paths to mask fields in nested serializers:

```python
class UserProfileSerializer(RoleMaskedModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'address']

        mask_fields = {
            "GUEST": {
                "email": "email",
                "address.street": "full",
                "address.postal_code": "partial_last:3",
            }
        }
```

## Custom Masking Strategies

### Using a Callable

```python
def custom_mask(value, mask_char="*"):
    """Mask middle portion of string."""
    if len(value) <= 4:
        return mask_char * len(value)
    keep = len(value) // 4
    return value[:keep] + mask_char * (len(value) - 2 * keep) + value[-keep:]

class MySerializer(RoleMaskedModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'secret_code']

        mask_fields = {
            "USER": {
                "secret_code": custom_mask,
            }
        }
```

### Using a Dictionary

```python
mask_fields = {
    "USER": {
        "phone": {
            "name": "partial_last",
            "kwargs": {"keep_last": 2}
        }
    }
}
```

## Configuration

Add these settings to your Django `settings.py`:

```python
# Default role attribute path (supports dotted paths like "profile.role")
DRM_ROLE_ATTR = "role"  # default

# Default masking character
DRM_MASK_CHAR = "*"  # default

# Default strategy when not specified
DRM_DEFAULT_STRATEGY = "full"  # default
```

## Role Resolution

The package resolves user roles using the following priority:

1. **Exact role match** - Uses the role-specific rules
2. **DEFAULT role** - Falls back to "DEFAULT" if defined
3. **ANONYMOUS role** - Falls back to "ANONYMOUS" if user is not authenticated
4. **No masking** - If no rules match, returns data unchanged

### Role Attribute Path

By default, the package looks for `user.role`. You can customize this:

```python
# settings.py
DRM_ROLE_ATTR = "profile.user_role"  # Supports dotted paths
```

Anonymous users automatically get the "ANONYMOUS" role.

## Advanced Usage

### Using the Mixin

```python
from rest_framework import serializers
from django_role_based_masking.serializers import RoleMaskedSerializerMixin

class CustomSerializer(RoleMaskedSerializerMixin, serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()

    # Define mask_fields as class attribute
    mask_fields = {
        "GUEST": {
            "email": "email"
        }
    }
```

### Programmatic Masking

```python
from django_role_based_masking.masking import apply_masking

data = {
    "name": "John Doe",
    "email": "john@example.com",
    "salary": "75000"
}

rules = {
    "EMPLOYEE": {
        "salary": "full"
    }
}

context = {"request": request}  # DRF request object

masked_data = apply_masking(data, rules, context)
```

## Requirements

- Python 3.10+
- Django 3.2+
- Django REST Framework 3.14+

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/gaikwadakshay79/django-role-based-masking.git
cd django-role-based-masking

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
ruff check .
ruff format .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## Support

- 📫 Issues: [GitHub Issues](https://github.com/gaikwadakshay79/django-role-based-masking/issues)
- 📖 Documentation: [README](https://github.com/gaikwadakshay79/django-role-based-masking#readme)

## Acknowledgments

Built with ❤️ for the Django and DRF community.
