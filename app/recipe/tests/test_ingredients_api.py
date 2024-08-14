"""
# app/recipe/tests/test_ingredients_api.py
Test for the Ingredients APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from ..serializers import IngredientSerializer

# Reverse URL Mapping for HTTP Request
INGREDIENT_URL = reverse('recipe:ingredient-list')


def create_user(email, password):
    """Create user in directly in db."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_ingredient(user, name):
    """Create ingredient directly in db."""
    return Ingredient.objects.create(user=user, name=name)


def ingredient_detail_url(ingredient_id):
    """Create ingredient directly in db."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientTestCase(TestCase):
    def setUp(self):
        """Setting up testing environment."""
        # Unauthorized client with no user
        self.client = APIClient()

    def test_unauthorized_access_ingredient_failure(self):
        """Test to check unauthorized access to ingredient must fail."""
        # Create user
        user = create_user('test@example.com', 'testPassword123')
        # Create ingredient directly in db
        create_ingredient(user=user, name='Potato')

        # HTTP Request to fetch ingredient
        res = self.client.get(INGREDIENT_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientTestCase(TestCase):
    """Test to check authorized access to ingredient must succeed."""
    def setUp(self):
        """Setting up testing environment for Authorized Test Client"""
        # create user & other user
        self.user = create_user('test@example.com', 'testPassword')
        self.other_user = create_user('otherUser@example.com', 'testPassword')

        # Authorize `self.user`
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_successfully(self):
        """Test to retrieve list ingredient's for authorized user."""
        # Create ingredient
        ingredient = create_ingredient(user=self.user, name='Tomoto')

        # HTTP Request
        res = self.client.get(INGREDIENT_URL)

        # Fetching data from db and serializing to JSON format
        db_data_fetched = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(db_data_fetched, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient.name, res.data[0]['name'])
        self.assertEqual(res.data, serializer.data)

    def test_patch_method_to_update_ingredients_successfully(self):
        """Test API call to delete an ingredient."""
        # Creating ingredient
        ingredient = create_ingredient(user=self.user, name='Onion')

        # HTTP Request
        payload = {'name': 'Peas'}
        url = ingredient_detail_url(ingredient.id)
        res = self.client.patch(url, payload, format='json')

        # Refresh data from db
        ingredient.refresh_from_db()

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(res.data['name'], ingredient.name)

    def test_delete_ingredient_from_db(self):
        """Test API call to delete an ingredient."""
        # Create an ingredient
        ingredient = create_ingredient(user=self.user, name='Carrot')

        # HTTP Request
        url = ingredient_detail_url(ingredient.id)
        res = self.client.delete(url)

        # Fetch ingredients of user
        db_ingredient_data = Ingredient.objects.filter(user=self.user)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(db_ingredient_data.exists())