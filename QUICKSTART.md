# Quick Start Guide

Get started with django-role-based-masking in 5 minutes!

## Installation

```bash
pip install django-role-based-masking
```

## Basic Setup

### 1. Add to Django Settings (Optional)

```python
# settings.py

# Configure role attribute path (default: "role")
DRM_ROLE_ATTR = "role"

# Configure masking character (default: "*")
DRM_MASK_CHAR = "*"

# Configure default strategy (default: "full")
DRM_DEFAULT_STRATEGY = "full"
```

### 2. Create Your Model

```python
# models.py
from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    ssn = models.CharField(max_length=11)
```

### 3. Create Serializer with Masking

```python
# serializers.py
from django_role_based_masking.serializers import RoleMaskedModelSerializer
from .models import Employee

class EmployeeSerializer(RoleMaskedModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'phone', 'salary', 'ssn']

        # Define masking rules per role
        mask_fields = {
            "ADMIN": {},  # Admins see everything

            "MANAGER": {
                "salary": "percentage:50",  # Mask 50% of salary
                "ssn": "partial_last:4",    # Show only last 4 digits
            },

            "EMPLOYEE": {
                "email": "email",           # Mask email local-part
                "phone": "partial_last:4",  # Show only last 4 digits
                "salary": "full",           # Fully mask salary
                "ssn": "full",              # Fully mask SSN
            },

            "ANONYMOUS": {
                "email": "full",
                "phone": "full",
                "salary": "full",
                "ssn": "full",
            }
        }
```

### 4. Use in Your View

```python
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeDetailView(APIView):
    def get(self, request, pk):
        employee = Employee.objects.get(pk=pk)
        serializer = EmployeeSerializer(
            employee,
            context={'request': request}  # Important: pass request context
        )
        return Response(serializer.data)
```

### 5. Set Up User Roles

Make sure your User model has a `role` field:

```python
# models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    role = models.CharField(
        max_length=50,
        choices=[
            ('ADMIN', 'Admin'),
            ('MANAGER', 'Manager'),
            ('EMPLOYEE', 'Employee'),
        ],
        default='EMPLOYEE'
    )
```

## Example Output

### Original Data

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "salary": "75000.00",
  "ssn": "123-45-6789"
}
```

### What ADMIN Sees

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "salary": "75000.00",
  "ssn": "123-45-6789"
}
```

### What MANAGER Sees

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "salary": "*****0.00",
  "ssn": "*******6789"
}
```

### What EMPLOYEE Sees

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "j*******@example.com",
  "phone": "*******890",
  "salary": "*********",
  "ssn": "***********"
}
```

## Available Masking Strategies

| Strategy         | Example              | Result               |
| ---------------- | -------------------- | -------------------- |
| `full`           | `"secret"`           | `"******"`           |
| `partial_last:4` | `"1234567890"`       | `"******7890"`       |
| `email`          | `"john@example.com"` | `"j***@example.com"` |
| `percentage:70`  | `"12345"`            | `"***45"`            |
| `noop`           | `"visible"`          | `"visible"`          |

## Nested Field Masking

```python
class UserProfileSerializer(RoleMaskedModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'address']

        mask_fields = {
            "GUEST": {
                "email": "email",
                "address.street": "full",           # Nested field
                "address.postal_code": "partial_last:3",
            }
        }
```

## Custom Masking Strategy

```python
def mask_middle(value, mask_char="*"):
    """Keep first and last 25%, mask middle."""
    length = len(str(value))
    if length <= 4:
        return str(value)
    keep = length // 4
    return value[:keep] + mask_char * (length - 2*keep) + value[-keep:]

class MySerializer(RoleMaskedModelSerializer):
    class Meta:
        model = MyModel
        fields = ['secret_code']

        mask_fields = {
            "USER": {
                "secret_code": mask_middle  # Use custom function
            }
        }
```

## Common Patterns

### Pattern 1: DEFAULT Fallback

```python
mask_fields = {
    "ADMIN": {},
    "DEFAULT": {  # Applies to any unknown role
        "sensitive_field": "full"
    }
}
```

### Pattern 2: Multiple Strategies

```python
mask_fields = {
    "USER": {
        "email": "email",
        "phone": "partial_last:4",
        "ssn": "full",
        "salary": "percentage:80"
    }
}
```

### Pattern 3: Conditional Masking

```python
mask_fields = {
    "ADMIN": {},           # No masking
    "MANAGER": {           # Partial masking
        "salary": "percentage:50"
    },
    "EMPLOYEE": {          # Full masking
        "salary": "full"
    }
}
```

## Troubleshooting

### Masking Not Working?

1. **Check request context**: Make sure you pass `context={'request': request}` to serializer
2. **Check user role**: Verify `request.user.role` exists and matches your rules
3. **Check field names**: Ensure field names in `mask_fields` match serializer fields

### Role Not Found?

- Package looks for `user.role` by default
- Configure `DRM_ROLE_ATTR` in settings if your role is elsewhere
- Example: `DRM_ROLE_ATTR = "profile.user_role"`

### Anonymous Users?

- Anonymous users automatically get `"ANONYMOUS"` role
- Define `"ANONYMOUS"` rules in `mask_fields` to handle them

## Next Steps

- Read the [full documentation](README.md)
- Check out [examples](docs/examples/)
- Learn about [custom strategies](docs/examples/custom_strategy.py)
- Explore [nested masking](docs/examples/nested_masking.py)

## Need Help?

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/gaikwadakshay79/django-role-based-masking/issues)
- 💡 [Request Features](https://github.com/gaikwadakshay79/django-role-based-masking/issues)

Happy masking! 🎭
