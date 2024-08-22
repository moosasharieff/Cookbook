"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

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


def create_tag(user: str, tag_name: str) -> Tag:
    """Create a tag."""
    return Tag.objects.create(user=user, name=tag_name)


def create_ingredient(user: str, ingredient_name: str) -> Ingredient:
    return Ingredient.objects.create(user=user, name=ingredient_name)


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
        # Creating a user and other user for testing
        self.user = create_user()
        self.other_user = create_user(
            email='other_user@example.com',
            password='OtherPass123')
        # Init Test client
        self.client = APIClient()
        self.other_client = APIClient()
        # Authenticate user
        self.client.force_authenticate(self.user)
        self.other_client.force_authenticate(self.other_user)

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

    def test_delete_other_user_recipe_failure(self):
        """Test resulting in failure when deteling other users recipe."""
        # Create a recipe
        recipe = create_recipe(user=self.user)

        # HTTP Request from `other_user` to delete `self.user`'s recipe
        url = recipe_detail_url(recipe.id)
        res = self.other_client.delete(url)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recipe_with_new_tag(self):
        """Test creating new recipe with new tag(s)."""
        # HTTP Request
        payload = {
            'title': 'Sample Title Name',
            'time_minutes': 25,
            'price': Decimal('10.5'),
            'description': 'This is a sample description.',
            'link': 'https://example.com',
            'tags': [
                {'name': 'Tomato'},
                {'name': 'Potato'}
            ]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        # Fetching db data
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]
        tags = recipe.tags

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(tags.count(), 2)
        for tag in payload['tags']:
            exists = tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tag(self):
        """Test creating recipe with existing tag(s)"""
        # Create a tag
        tag = create_tag(user=self.user, tag_name='Carrot')

        # HTTP Request
        payload = {
            'title': 'Sample Title Name',
            'time_minutes': 25,
            'price': Decimal('10.5'),
            'description': 'This is a sample description.',
            'link': 'https://example.com',
            'tags': [
                {'name': 'Tomato'},
                {'name': 'Potato'},
                {'name': 'Carrot'},
            ]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        # Fetch db data
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]
        tags = recipe.tags

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(tags.count(), 3)
        for tag in payload['tags']:
            exists = Tag.objects.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(exists)

    def test_update_recipe_adding_new_tag(self):
        """Test update recipe adding new tag."""
        # Create recipe directly in db
        recipe = create_recipe(user=self.user)

        # HTTP Request
        payload = {
            'tags': [
                {'name': 'Indian'}
            ]
        }
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        # Refresh db
        recipe.refresh_from_db()
        tags = recipe.tags

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tags.count(), 1)
        for tag in payload['tags']:
            exists = Tag.objects.filter(
                user=self.user,
                name=tag['name']
            ).exists()

            self.assertTrue(exists)

    def test_update_recipe_with_existing_tag(self):
        """Test to update recipe with an existing tag."""
        # Create Recipe and Tag
        recipe = create_recipe(user=self.user)
        tag = create_tag(user=self.user, tag_name='Apple')

        # HTTP Request
        payload = {
            'tags': [
                {'name': 'Apple'},
            ]
        }
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing out all all tags in a recipe."""
        # Create recipe and tags directly in db
        recipe = create_recipe(user=self.user)
        tag1 = create_tag(user=self.user, tag_name='Carrot')
        tag2 = create_tag(user=self.user, tag_name='Brinjal')
        recipe.tags.add(tag1)
        recipe.tags.add(tag2)

        # HTTP Request
        payload = {'tags': []}
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_and_ingredient(self):
        """Test creating new recipe with new ingredient."""
        # HTTP Request
        payload = {
            'title': 'Sample Title Name',
            'time_minutes': 25,
            'price': Decimal('10.5'),
            'description': 'This is a sample description.',
            'link': 'https://example.com',
            'tags': [
                {'name': 'Dinner'},
                {'name': 'Indian'}
            ],
            'ingredients': [
                {'name': 'Tomato'}
            ]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        response_data = res.data['ingredients'][0]

        # Fetch data from db
        db_data = Recipe.objects.filter(user=self.user)
        serialized = RecipeSerializer(db_data, many=True)
        serialized_data = serialized.data[0]['ingredients'][0]

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serialized.data[0])
        self.assertEqual(response_data['id'], serialized_data['id'])
        self.assertEqual(response_data['name'], serialized_data['name'])

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating new recipe with existing ingredient"""
        # Create an ingredient
        ingredient = create_ingredient(
            user=self.user,
            ingredient_name='Potato'
        )

        # HTTP Request
        payload = {
            'title': 'Sample Title Name',
            'time_minutes': 25,
            'price': Decimal('10.5'),
            'description': 'This is a sample description.',
            'link': 'https://example.com',
            'ingredients': [
                {'name': 'Potato'},
            ]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')
        response_data = res.data['ingredients'][0]

        # Fetch db data
        db_data = Recipe.objects.filter(user=self.user)
        serialized = RecipeSerializer(db_data, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serialized.data[0])
        self.assertEqual(response_data['name'], ingredient.name)
        self.assertEqual(response_data['id'], ingredient.id)

    def test_retrieve_existing_recipe_with_existing_ingredient(self):
        """Test reading existing recipe with existing ingredient"""
        # Create Recipe and Ingredient and add ingredient to it.
        ingredient = create_ingredient(user=self.user,
                                       ingredient_name='Banana')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        # HTTP Request
        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)
        res_data = res.data['ingredients'][0]

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], recipe.id)
        self.assertEqual(res_data['id'], ingredient.id)
        self.assertEqual(res_data['name'], ingredient.name)

    def test_retrieving_existing_recipe_with_multiple_ingredients(self):
        """Test reading existing recipe with multiple existing ingredient"""
        # Create Recipe and Ingredient and add ingredient to it.
        ingredient1 = create_ingredient(user=self.user,
                                        ingredient_name='Banana')
        ingredient2 = create_ingredient(user=self.user,
                                        ingredient_name='Apple')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)
        recipe.ingredients.add(ingredient2)

        # HTTP Request
        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)
        res_data = res.data['ingredients']

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], recipe.id)
        self.assertEqual(res_data[0]['id'], ingredient1.id)
        self.assertEqual(res_data[0]['name'], ingredient1.name)
        self.assertEqual(res_data[1]['id'], ingredient2.id)
        self.assertEqual(res_data[1]['name'], ingredient2.name)

    def test_update_recipe_with_new_ingredient(self):
        """Test Updating existing recipe with new ingredient"""
        # Create recipe
        recipe = create_recipe(user=self.user)

        # HTTP Request
        payload = {
            'ingredients': [
                {'name': 'Brinjal'},
                {'name': 'Carrot'},
            ]
        }

        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Asserting to check ingredients present in recipe?
        for ingredient in payload['ingredients']:
            exists = Ingredient.objects.filter(
                user=self.user,
                name=ingredient['name']
            ).exists()

            self.assertTrue(exists)

    def test_update_recipe_with_existing_ingredient(self):
        """Test Updating existing recipe with existing ingredient"""
        # Create recipe and ingredients
        recipe = create_recipe(user=self.user)
        create_ingredient(user=self.user, ingredient_name='Carrot')
        create_ingredient(user=self.user, ingredient_name='Banana')

        # HTTP Request
        payload = {
            'ingredients': [
                {'name': 'Banana'},
                {'name': 'Carrot'},
            ]
        }

        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Asserting to check ingredients present in recipe?
        for ingredient in payload['ingredients']:
            exists = Ingredient.objects.filter(
                user=self.user,
                name=ingredient['name']
            ).exists()

            self.assertTrue(exists)

    def test_delete_recipe_with_ingredient(self):
        """Test deleting existing recipe which already has an ingredient"""
        # Create recipe and ingredient directly in db
        # add ingredient to the recipe
        recipe = create_recipe(user=self.user)
        ingredient = create_ingredient(user=self.user,
                                       ingredient_name='Potato')
        recipe.ingredients.add(ingredient)

        # HTTP Request
        url = recipe_detail_url(recipe.id)
        res = self.client.delete(url)

        # Fetch data from db
        recipe_exists = Recipe.objects.filter(
            user=self.user,
            id=recipe.id).exists()

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(recipe_exists)
