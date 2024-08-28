"""
Test cases for nutrient APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model # noqa
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Nutrient # noqa

from ..serializers import NutrientSerializer # noqa


class BaseClass:
    NUTRIENT_URL = reverse('recipe:nutrient-list')

    def create_user(self, email: str, password: str) -> get_user_model:
        """Private Method: Create user directly in the database."""
        return get_user_model().objects.create(
            email=email, password=password
        )

    def create_nutrient(self, user: str, name: str, grams: float) -> Nutrient:
        "Private Method: Create nutrient directly in the database."
        return Nutrient.objects.create(
            user=user, name=name, grams=Decimal(grams)
        )


class PublicNutrientAPITests(TestCase, BaseClass):
    """Public test cases which does not
    require user authentication."""
    def setUp(self):
        """Setting up testing environment."""
        # Create a client
        self.client = APIClient()

    def test_retrieve_nutrient_list(self):
        """Test retriving list of nutrients."""
        # HTTP Request
        res = self.client.get(self.NUTRIENT_URL)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateNutrientAPITests(TestCase, BaseClass):
    """Private test cases which require user authentication.

    # Possible CRUD API test cases
    C ->
    1. Create nutrient
    R ->
    2. Read single nutrient
    3. Read multiple nutrients
    U ->
    4. Update an existing nutrient with PATCH METHOD
    5. Update a new nutrient PATCH METHOD
    6. Update an existing nutrient with PUT METHOD
    7. Update a new nutrient with PUT METHOD
    D ->
    8. Delete the nutrient
    """
    def setUp(self):
        """Setting up testing environment."""
        # Create user
        self.user = self.create_user(
            email='test@example.com', password='testPass@123'
        )
        # Create API Test Client
        self.client = APIClient()
        # Authenticate user with the test client
        self.client.force_authenticate(self.user)

    def test_list_all_nutrients_of_user(self):
        """Test read ingredient via API call."""
        # Create nutrient directly in the db
        nutrient = self.create_nutrient(
            user=self.user, name='Calcium', grams=5.00)

        # HTTP Request
        res = self.client.get(self.NUTRIENT_URL)

        # Formatting data
        gram_val = float(nutrient.grams)
        gram_val = format(gram_val, '.2f')

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], nutrient.id)
        self.assertEqual(res.data[0]['name'], nutrient.name)
        self.assertEqual(res.data[0]['grams'], gram_val)
