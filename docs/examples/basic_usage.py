"""
Basic usage example for django-role-based-masking.

This example demonstrates how to use RoleMaskedModelSerializer
to mask sensitive fields based on user roles.
"""

from django.db import models
from rest_framework.response import Response
from rest_framework.views import APIView

from django_role_based_masking.serializers import RoleMaskedModelSerializer


# Example Model
class Employee(models.Model):
    """Employee model with sensitive fields."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    ssn = models.CharField(max_length=11)

    class Meta:
        app_label = "example"


# Example Serializer with Role-Based Masking
class EmployeeSerializer(RoleMaskedModelSerializer):
    """
    Employee serializer with role-based field masking.

    Different roles see different levels of data:
    - ADMIN: Sees all data unmasked
    - MANAGER: Sees partial masking on sensitive fields
    - EMPLOYEE: Sees most fields masked
    - ANONYMOUS: Sees all sensitive fields fully masked
    """

    class Meta:
        model = Employee
        fields = ["id", "name", "email", "phone", "salary", "ssn"]

        # Define masking rules per role
        mask_fields = {
            "ADMIN": {},  # No masking for admins
            "MANAGER": {
                "ssn": "partial_last:4",  # Show last 4 digits: ***-**-6789
                "salary": "percentage:50",  # Mask 50% from left: ***50.00
            },
            "EMPLOYEE": {
                "email": "email",  # Mask local part: j***@example.com
                "phone": "partial_last:4",  # Show last 4: ******7890
                "salary": "full",  # Fully masked: *******
                "ssn": "full",  # Fully masked: ***********
            },
            "ANONYMOUS": {
                "email": "full",
                "phone": "full",
                "salary": "full",
                "ssn": "full",
            },
        }


# Example Usage in a View


class EmployeeDetailView(APIView):
    """
    API view that returns employee data with role-based masking.
    """

    def get(self, request, pk):
        employee = Employee.objects.get(pk=pk)
        serializer = EmployeeSerializer(employee, context={"request": request})
        return Response(serializer.data)


# Example Output for Different Roles
"""
Original Data:
{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "salary": "75000.00",
    "ssn": "123-45-6789"
}

ADMIN sees:
{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "salary": "75000.00",
    "ssn": "123-45-6789"
}

MANAGER sees:
{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "salary": "***50.00",
    "ssn": "*******6789"
}

EMPLOYEE sees:
{
    "id": 1,
    "name": "John Doe",
    "email": "j*******@example.com",
    "phone": "*******890",
    "salary": "********",
    "ssn": "***********"
}

ANONYMOUS sees:
{
    "id": 1,
    "name": "John Doe",
    "email": "*********************",
    "phone": "************",
    "salary": "********",
    "ssn": "***********"
}
"""
