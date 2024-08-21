
from django.contrib.auth import get_user_model # noqa
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicTestsIngredientAPI(TestCase):
    """Public / Unauthorized Test cases for ingredient api."""
    def setUp(self):
        """Setting up testing environment."""
        # Instantiating API Client
        self.client = APIClient()

    def test_retrieving_ingredient_list_failure(self):
        """Test retrieving ingredient of a user resulting in a failure."""

        # HTTP Request
        res = self.client.get(INGREDIENT_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
