
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from ..serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


def create_user(email: str, password: str) -> get_user_model:
    return get_user_model().objects.create_user(email=email, password=password)


def create_ingredient(user: str, name: str) -> Ingredient:
    return Ingredient.objects.create(user=user, name=name)


def ingredient_detail_url(ingredient_id: int) -> reverse:
    """Return a auto-generated URL string to Update/Delete
    a particular ingredient."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


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


class PrivateTestsIngredientAPI(TestCase):
    """User authorized test cases.
    # Possible API test cases on CRUD
    0. C -> Create an ingredient
    1. R -> Read list of ingredients of a user
    2. U -> Update a particular ingredient of a user
    3. D -> Delete a particular ingredient of a user
    """

    def setUp(self):
        """Setting up test environment."""
        # Create user directly in db
        self.user = create_user('test@example.com', 'password@123')
        # Instantiate Test Client
        self.client = APIClient()
        # Authorized user
        self.client.force_authenticate(self.user)

    def test_list_ingredients(self):
        """Test returning list of ingredient for authenticated users."""
        # Create ingredient directly in db
        ingredient = create_ingredient(user=self.user, name='Potato')

        # HTTP Request
        res = self.client.get(INGREDIENT_URL)

        # Serialize JSON Data with Db Data
        ingredients = Ingredient.objects.all().order_by('-name')
        serialized = IngredientSerializer(ingredients, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serialized.data, res.data)
        self.assertEqual(res.data[0]['id'], ingredient.id)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_update_ingredient(self):
        """Test update ingredient."""
        # Create ingredient directly in the db
        ingredient = create_ingredient(user=self.user, name='Tomato')

        # HTTP Request
        payload = {
            'name': 'Onion'
        }
        url = ingredient_detail_url(ingredient.id)
        res = self.client.put(url, payload, format='json')

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], ingredient.id)
        self.assertEqual(res.data['name'], payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        # Create ingredient directly in the db
        ingredient = create_ingredient(user=self.user, name='Onion')

        # HTTP Request
        url = ingredient_detail_url(ingredient.id)
        res = self.client.delete(url)

        # Fetching data from db
        db_data = Ingredient.objects.filter(user=self.user)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(db_data.exists())

    def test_create_ingredient(self):
        """Test create ingredient via API."""
        # Payload
        payload = {
            'name': 'Onion'
        }
        # HTTP Request
        res = self.client.post(INGREDIENT_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], payload['name'])
