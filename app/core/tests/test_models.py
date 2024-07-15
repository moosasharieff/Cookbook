"""
# app/core/tests/test_models.py

Testing models.
"""

from django.test import TestCase
# Default user model for Auth
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """
        Test creating a user with email instead of username is
        successful.
        """
        email = "test@example.com"
        password = "testPassword123"

        # Need to implement email functionality in get_user_model()
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        # We use user.check_password() as we use hashing to check password
        self.assertTrue(user.check_password(password))
