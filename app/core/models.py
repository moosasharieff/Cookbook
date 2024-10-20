"""
# app/core/models.py
Models for Django application
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def recipe_image_file_path(instance, filename: str) -> str:
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    # generate path
    return os.path.join('uploads', 'recipe', filename)


def ingredient_image_file_path(instance, filename: str) -> str:
    """Generate file path for new ingredient image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    # Generate path
    return os.path.join('uploads', 'ingredient', filename)


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

    def create_superuser(self, email, password):
        """Create's a User a superuser"""
        user = self.create_user(email, password)
        # Adding superuser functionality
        user.is_staff = True
        user.is_superuser = True
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


class Recipe(models.Model):
    """Class for creating recipes from the user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        """Returns string representation of 'Recipe' model."""
        return self.title


class Tag(models.Model):
    """Class for creating tags and associating it with Recipe class."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        """Returns tags name."""
        return self.name


class Ingredient(models.Model):
    """Schema for Ingredient database."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    nutrients = models.ManyToManyField('Nutrient')
    image = models.ImageField(null=True, upload_to=ingredient_image_file_path)

    def __str__(self):
        """String representation on Ingredient database."""
        return self.name


class Nutrient(models.Model):
    """Schema for Nutrient Database"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=25)
    grams = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
