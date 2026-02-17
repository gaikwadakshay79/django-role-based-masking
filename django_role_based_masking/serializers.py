"""
DRF serializer mixins and base classes for django-role-based-masking.
"""

from rest_framework import serializers

from django_role_based_masking.masking import apply_masking


class RoleMaskedSerializerMixin:
    """
    Mixin for DRF serializers to apply role-based field masking.

    Usage:
        class MySerializer(RoleMaskedSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = MyModel
                fields = ['id', 'name', 'email']
                mask_fields = {
                    "ADMIN": {},
                    "USER": {
                        "email": "email"
                    }
                }
    """

    def to_representation(self, instance):
        """
        Override to_representation to apply masking after serialization.

        Args:
            instance: Model instance or data to serialize

        Returns:
            Serialized and masked data dictionary
        """
        # Get the standard representation
        data = super().to_representation(instance)

        # Get masking rules from Meta.mask_fields or self.mask_fields
        mask_fields = None
        if hasattr(self, "Meta") and hasattr(self.Meta, "mask_fields"):
            mask_fields = self.Meta.mask_fields
        elif hasattr(self, "mask_fields"):
            mask_fields = self.mask_fields

        # If no masking rules, return data unchanged
        if not mask_fields:
            return data

        # Only apply masking if request exists in context
        if "request" not in self.context:
            return data

        # Apply masking
        return apply_masking(data, mask_fields, self.context)


class RoleMaskedModelSerializer(RoleMaskedSerializerMixin, serializers.ModelSerializer):
    """
    ModelSerializer with built-in role-based field masking.

    Usage:
        class EmployeeSerializer(RoleMaskedModelSerializer):
            class Meta:
                model = Employee
                fields = ['id', 'name', 'email', 'salary']
                mask_fields = {
                    "ADMIN": {},
                    "MANAGER": {
                        "salary": "percentage:50"
                    },
                    "EMPLOYEE": {
                        "salary": "full"
                    }
                }
    """

    pass


class RoleMaskedSerializer(RoleMaskedSerializerMixin, serializers.Serializer):
    """
    Serializer with built-in role-based field masking.

    Usage:
        class DataSerializer(RoleMaskedSerializer):
            name = serializers.CharField()
            email = serializers.EmailField()

            mask_fields = {
                "GUEST": {
                    "email": "email"
                }
            }
    """

    pass
