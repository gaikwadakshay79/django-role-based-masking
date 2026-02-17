"""
Test models for django-role-based-masking tests.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class TestUserManager(BaseUserManager):
    """Manager for TestUser model."""

    def create_user(self, username, role="USER", password=None):
        """Create and return a user."""
        user = self.model(username=username, role=role)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


class TestUser(AbstractBaseUser):
    """
    Custom user model for testing with a role field.
    """

    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=50, default="USER")
    is_active = models.BooleanField(default=True)

    objects = TestUserManager()

    USERNAME_FIELD = "username"

    class Meta:
        app_label = "testapp"

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        return True


class EmployeeProfile(models.Model):
    """
    Employee profile model for testing masking functionality.
    """

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    salary = models.CharField(max_length=20)
    ssn = models.CharField(max_length=20)
    pan = models.CharField(max_length=20)

    # JSON field for nested data (simplified as CharField for compatibility)
    address_street = models.CharField(max_length=200, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_postal_code = models.CharField(max_length=20, blank=True)

    class Meta:
        app_label = "testapp"

    def __str__(self):
        return self.name
