"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from ..serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe_id):
    """Returns custom recipe URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_user(**params):
    """Creates user directly in db."""
    defaults = {
        'email': 'test@example.com',
        'password': 'testPassword123',
    }

    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)

    return user


def create_recipe(user, **params):
    """Create recipe directly in db."""
    defaults = {
        'title': 'Sample Title Name',
        'time_minutes': 25,
        'price': Decimal('10.5'),
        'description': 'This is a sample description.',
        'link': 'https://example.com',
    }

    defaults.update(**params)
    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


class PublicRecipeAPITests(TestCase):
    """Test case of Recipe API for un-authorized user."""

    def setUp(self):
        """Setting up test environment."""
        # Init Test client
        self.client = APIClient()

    def test_retrieve_recipe_list_failure(self):
        """Test retrieving recipe list to fail."""
        res = self.client.get(RECIPE_URL)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test cases of Recipe APIs for autorized users."""

    def setUp(self):
        """Setting up test environment."""
        # Creating a user
        self.user = create_user()
        # Init Test client
        self.client = APIClient()
        # Authenticate user
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieve recipes."""
        # Creating recipes directly in db
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        # HTTP Request to Endpoint
        res = self.client.get(RECIPE_URL)

        # Fetching data from db
        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)

        # Assertion
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipe_for_specific_user(self):
        """Test retrieving data for specific user."""
        # Creating users
        params = {
            'email': 'test2@example.com',
            'password': 'TestPassword321'
        }
        other_user = create_user(**params)

        # Creating recipes
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        # HTTP Request to Endpoint
        res = self.client.get(RECIPE_URL)

        # Fetch details from db
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipe_details(self):
        # Create a recipe directly in db
        recipe = create_recipe(user=self.user)

        # Creating Custom URL for recipe detail
        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)

        # Serialize recipe details to match with retrieved data
        serializer = RecipeDetailSerializer(recipe)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_api(self):
        """Test create recipe from API."""
        payload = {
            'title': 'Sample Recipe',
            'time_minutes': 35,
            'price': Decimal('3.99'),
        }

        # HTTP Request to create the recipe
        res = self.client.post(RECIPE_URL, payload)

        # Fetch recipe data from db
        recipe_data = Recipe.objects.get(id=res.data['id'])

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipe_data.user, self.user)

        # Asserting values
        for key, value in payload.items():
            self.assertEqual(getattr(recipe_data, key), value)

    def test_partial_update(self):
        """Test updating the fields of the recipe partially."""
        # Create a new recipe
        recipe = create_recipe(user=self.user)

        # Creating a payload
        payload = {
            'title': 'Updated sample title',
            'time_minutes': 20,
        }

        # HTTP Request to make changes
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload)

        # Refreshing recipe data from db
        recipe.refresh_from_db()

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test updating all the fields of the recipe."""
        # Creating a recipe
        recipe = create_recipe(user=self.user)

        # Payload to be updated
        payload = {
            'title': 'UpdatedSample Title Name',
            'time_minutes': 15,
            'price': Decimal('9.5'),
            'description': 'Updated: This is a sample description.',
            'link': 'https://updated_example.com',
        }

        # HTTP 'PUT' Request to update all fields
        url = recipe_detail_url(recipe.id)
        res = self.client.put(url, payload)

        # Refreshing the recipe fields from db
        recipe.refresh_from_db()

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.user, self.user)
        # Iterating and asserting
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

    def test_updating_user_in_recipe_returns_no_success(self):
        """Test changing creator of recipe returns no success."""
        # Creating user and adding authentication to it.
        creds = {
                'email': 'otherUser@example.com',
                'password': 'DiffPassword123',
            }
        new_user = create_user(**creds)

        new_client = APIClient()
        new_client.force_authenticate(new_user)

        # Create a recipe
        recipe = create_recipe(user=self.user)

        # Creating Payload
        payload = {
            'user': new_user.id,
        }

        # HTTP 'PATCH' Request to update the user
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        # Refreshing the user in db
        recipe.refresh_from_db()

        # Assertion
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        # Creating a recipe
        recipe = create_recipe(user=self.user)

        # HTTP Request to delete the recipe
        url = recipe_detail_url(recipe.id)
        res = self.client.delete(url)

        # Fetching recipe data from db
        is_recipe_present = Recipe.objects.filter(id=recipe.id).exists()

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(is_recipe_present)
