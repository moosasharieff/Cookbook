"""
# app/core/models.py
Models for Django application
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for User model."""

    def create_user(self, email, password=None, **extra_field):
        """Create, save and return a new user."""
        # Self.model call `class: User` and inputs the attr
        if not email:
            raise ValueError("Email was not provided.")
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Creates User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Create the user
    objects = UserManager()

    REQUIRED_FIELDS = []

    # Overriding in system to use `email` instead of
    # username when Authenticating.
    USERNAME_FIELD = "email"
