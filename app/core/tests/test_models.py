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


    def test_user_email_normalized(self):
        """Emails provided by the users is Normalized
        and then saved into the db."""
        sample_email = [
            ["Sample@EXAMPLE.COM", "Sample@example.com"],
            ["SamPle@Example.COM", "SamPle@example.com"],
            ["SamPLEe@example.COM", "SamPLEe@example.com"],
            ["SAMPLE@EXAMPLE.com", "SAMPLE@example.com"],
        ]

        # Test Cases
        for inc_email, exp_email in sample_email:
            user = get_user_model().objects.create_user(inc_email, "samplePassword123")
            self.assertEqual(user.email, exp_email)