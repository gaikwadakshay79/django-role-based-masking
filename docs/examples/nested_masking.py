"""
Nested field masking example for django-role-based-masking.

This example demonstrates how to mask fields in nested serializers
using dotted path notation.
"""

from django.db import models
from rest_framework import serializers

from django_role_based_masking.serializers import RoleMaskedModelSerializer


# Example Models
class Address(models.Model):
    """Address model."""

    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)

    class Meta:
        app_label = "example"


class UserProfile(models.Model):
    """User profile with nested address."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    class Meta:
        app_label = "example"


# Nested Serializers
class AddressSerializer(serializers.ModelSerializer):
    """Standard address serializer (no masking logic here)."""

    class Meta:
        model = Address
        fields = ["street", "city", "state", "postal_code", "country"]


class UserProfileSerializer(RoleMaskedModelSerializer):
    """
    User profile serializer with nested address masking.

    Uses dotted path notation to mask nested fields:
    - "address.street" masks the street field in the nested address
    - "address.postal_code" masks the postal code
    """

    address = AddressSerializer()

    class Meta:
        model = UserProfile
        fields = ["id", "name", "email", "phone", "address"]

        mask_fields = {
            "ADMIN": {},
            "USER": {
                "email": "email",
                "phone": "partial_last:4",
                "address.street": "full",  # Mask nested street
                "address.postal_code": "partial_last:3",  # Show last 3 of postal code
            },
            "GUEST": {
                "email": "full",
                "phone": "full",
                "address.street": "full",
                "address.city": "full",
                "address.postal_code": "full",
            },
        }


# Example with Deeply Nested Data
class ContactInfo(models.Model):
    """Contact information model."""

    phone = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        app_label = "example"


class Profile(models.Model):
    """Profile with contact info."""

    bio = models.TextField()
    contact = models.ForeignKey(ContactInfo, on_delete=models.CASCADE)

    class Meta:
        app_label = "example"


class User(models.Model):
    """User with nested profile."""

    username = models.CharField(max_length=100)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        app_label = "example"


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ["phone", "email"]


class ProfileSerializer(serializers.ModelSerializer):
    contact = ContactInfoSerializer()

    class Meta:
        model = Profile
        fields = ["bio", "contact"]


class UserSerializer(RoleMaskedModelSerializer):
    """
    User serializer with deeply nested masking.

    Demonstrates masking at multiple nesting levels:
    - profile.contact.phone
    - profile.contact.email
    """

    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "profile"]

        mask_fields = {
            "ADMIN": {},
            "USER": {
                "profile.contact.phone": "partial_last:4",
                "profile.contact.email": "email",
            },
            "GUEST": {
                "profile.bio": "full",
                "profile.contact.phone": "full",
                "profile.contact.email": "full",
            },
        }


# Example Output
"""
Original Data:
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "address": {
        "street": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA"
    }
}

USER sees:
{
    "id": 1,
    "name": "John Doe",
    "email": "j***@example.com",
    "phone": "******7890",
    "address": {
        "street": "****************",
        "city": "New York",
        "state": "NY",
        "postal_code": "**001",
        "country": "USA"
    }
}

GUEST sees:
{
    "id": 1,
    "name": "John Doe",
    "email": "****************",
    "phone": "**********",
    "address": {
        "street": "****************",
        "city": "********",
        "state": "NY",
        "postal_code": "*****",
        "country": "USA"
    }
}
"""


# Example with List of Nested Objects
class OrderItem(models.Model):
    """Order item model."""

    product_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    class Meta:
        app_label = "example"


class Order(models.Model):
    """Order with multiple items."""

    order_number = models.CharField(max_length=50)
    customer_email = models.EmailField()

    class Meta:
        app_label = "example"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product_name", "price", "quantity"]


class OrderSerializer(RoleMaskedModelSerializer):
    """
    Order serializer that masks prices in nested items.

    When masking "items.price", it will mask the price field
    in all items in the list.
    """

    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "order_number", "customer_email", "items"]

        mask_fields = {
            "ADMIN": {},
            "CUSTOMER": {
                "customer_email": "email",
            },
            "GUEST": {
                "customer_email": "full",
                "items.price": "full",  # Masks price in all items
            },
        }
