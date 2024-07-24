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