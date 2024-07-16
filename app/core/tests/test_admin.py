"""
# app/core/tests/test_admin.py
Tests for the Django admin modifications.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create user and client."""
        self.client = Client()

        # Admin
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='Password123'
        )
        self.client.force_login(self.admin_user)

        # Ordinary User
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='Password123',
            name='Test User'
        )

    def test_users_list(self):
        """Test users are listed on page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        # Assertions
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        # core -> Section, user -> Group, change -> Edit
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        # Assertions
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test create user page from Django Admin Page."""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        # Assertions
        self.assertEqual(res.status_code, 200)
