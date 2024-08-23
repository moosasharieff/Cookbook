"""
Test cases for nutrient APIs.
"""

from django.contrib.auth import get_user_model # noqa
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Nutrient # noqa

from ..serializers import NutrientSerializer # noqa

NUTRIENT_URL = reverse('recipe:nutrient-list')


class PublicNutrientAPITests(TestCase):
    """Public test cases which does not
    require user authentication."""
    def setUp(self):
        """Setting up testing environment."""
        # Create a client
        self.client = APIClient()

    def test_retrieve_nutrient_list(self):
        """Test retriving list of nutrients."""
        # HTTP Request
        res = self.client.get(NUTRIENT_URL)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
