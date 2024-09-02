
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Nutrient

from ..serializers import IngredientSerializer


class TestRequirementsClass:
    """Attributes and Methods which can be inherited and used or
    used directly by calling the class."""
    _INGREDIENT_URL = reverse('recipe:ingredient-list')

    def _create_user(self, email: str, password: str) -> get_user_model:
        return get_user_model().objects.create_user(
            email=email, password=password
        )

    def _create_ingredient(self,
                           user: get_user_model,
                           name: str) -> Ingredient:
        return Ingredient.objects.create(user=user, name=name)

    def _ingredient_detail_url(self, ingredient_id: int) -> reverse:
        """Return a auto-generated URL string to Update/Delete
        a particular ingredient."""
        return reverse('recipe:ingredient-detail', args=[ingredient_id])

    def _create_nutrient(self,
                         user: get_user_model,
                         nutrient_name: str,
                         grams: float) -> Nutrient:

        return Nutrient.objects.create(user=user,
                                       name=nutrient_name,
                                       grams=Decimal(grams))


class PublicTestsIngredientAPI(TestCase, TestRequirementsClass):
    """Public / Unauthorized Test cases for ingredient api."""
    def setUp(self):
        """Setting up testing environment."""
        # Instantiating API Client
        self.client = APIClient()

    def test_retrieving_ingredient_list_failure(self):
        """Test retrieving ingredient of a user resulting in a failure."""

        # HTTP Request
        res = self.client.get(self._INGREDIENT_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestsIngredientAPI(TestCase, TestRequirementsClass):
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
        self.user = self._create_user('test@example.com', 'password@123')
        # Instantiate Test Client
        self.client = APIClient()
        # Authorized user
        self.client.force_authenticate(self.user)

    def test_list_ingredients(self):
        """Test returning list of ingredient for authenticated users."""
        # Create ingredient directly in db
        ingredient = self._create_ingredient(user=self.user, name='Potato')

        # HTTP Request
        res = self.client.get(self._INGREDIENT_URL)

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
        ingredient = self._create_ingredient(user=self.user, name='Tomato')

        # HTTP Request
        payload = {
            'name': 'Onion'
        }
        url = self._ingredient_detail_url(ingredient.id)
        res = self.client.put(url, payload, format='json')

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], ingredient.id)
        self.assertEqual(res.data['name'], payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        # Create ingredient directly in the db
        ingredient = self._create_ingredient(user=self.user, name='Onion')

        # HTTP Request
        url = self._ingredient_detail_url(ingredient.id)
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
        res = self.client.post(self._INGREDIENT_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], payload['name'])

    def test_list_single_ingredient(self):
        """Test retrieve single ingredient upon entering ingredient id."""
        # Create an ingredient in db
        ingredient = self._create_ingredient(user=self.user, name='Banana')

        # HTTP Request
        url = self._ingredient_detail_url(ingredient.id)
        res = self.client.get(url)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateTestsIngredientAndNutrientsAPI(TestCase, TestRequirementsClass):
    """Test cases for Ingredients and Nutrients."""
    # Todo: Possible test cases for Ingredients and Nutrients.
    # Todo: 1. Create new nutrient with new ingredient
    # Todo: 2. Create new ingredient with existing nutrient
    # Todo: 5. Partially update nutrient on an ingredient.
    # Todo: 6. Fully update nutrient on an ingredient.
    # Todo: 7. Delete ingredient with nutrient.

    def setUp(self):
        """Setting up testing environment."""
        # Create user
        self.user = self._create_user('test@example.com', 'password@123')
        # API Test Client
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_with_single_nutrient(self):
        """Test reading ingredient with a single nutrient"""
        # Create an ingredient
        ingredient = self._create_ingredient(user=self.user, name='Onion')
        # Create nutrient
        nutrient = self._create_nutrient(user=self.user,
                                         nutrient_name='Calcium',
                                         grams='2.99')

        # Adding nutrient to ingredient
        ingredient.nutrients.add(nutrient)

        # HTTP Request
        url = self._ingredient_detail_url(ingredient.id)
        res = self.client.get(url)

        # Parsing data
        res_data = res.data['nutrients'][0]

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], ingredient.id)
        self.assertEqual(res_data['id'], nutrient.id)
        self.assertEqual(res_data['name'], nutrient.name)
        self.assertEqual(res_data['grams'], str(nutrient.grams))

    def test_retrieve_ingredient_with_multiple_nutrients(self):
        """Test retrieving a single ingredient with multiple
        nutrients."""
        # Create ingredients
        ingredient = self._create_ingredient(
            user=self.user, name='Potato'
        )

        # Creating nutrients
        nutrient1 = self._create_nutrient(
            user=self.user, nutrient_name='Calcium', grams='0.99'
        )
        nutrient2 = self._create_nutrient(
            user=self.user, nutrient_name='Potasium', grams='1.15'
        )

        # Adding nutrients to ingredients
        ingredient.nutrients.add(nutrient1)
        ingredient.nutrients.add(nutrient2)

        # HTTP Request
        url = self._ingredient_detail_url(ingredient.id)
        res = self.client.get(url)

        # Parse data
        res_nutrients = res.data['nutrients']

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], ingredient.id)
        # Validating 1st nutrient
        self.assertEqual(res_nutrients[0]['id'], nutrient1.id)
        self.assertEqual(res_nutrients[0]['name'], nutrient1.name)
        self.assertEqual(res_nutrients[0]['grams'], str(nutrient1.grams))
        # Validating 2nd nutrient
        self.assertEqual(res_nutrients[1]['id'], nutrient2.id)
        self.assertEqual(res_nutrients[1]['name'], nutrient2.name)
        self.assertEqual(res_nutrients[1]['grams'], str(nutrient2.grams))

    def test_create_ingredient_with_existing_nutrient(self):
        """Test creating new recipe with existing ingredient"""
        # Create nutrient
        nutrient = self._create_nutrient(user=self.user,
                                         nutrient_name='Calcium',
                                         grams='3.23')

        # HTTP Request
        payload = {
            'name': 'Banana',
            'nutrients': [
                {'name': 'Calcium', 'grams': '3.23'},
            ]
        }

        res = self.client.post(self._INGREDIENT_URL, payload, format='json')
        response_data = res.data['nutrients'][0]

        # Fetch db data
        db_data = Ingredient.objects.filter(user=self.user)
        serialized = IngredientSerializer(db_data, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serialized.data[0])
        self.assertEqual(response_data['name'], nutrient.name)
        self.assertEqual(response_data['id'], nutrient.id)

    def test_create_new_ingredient_with_new_nutrients(self):
        """Test creating new ingredient with multiple new nutrients"""
        # Payload
        payload = {
            'name': 'Orange',
            'nutrients': [
                {'name': 'Vitamin C', 'grams': '4.04'},
                {'name': 'Vitamin A', 'grams': '2.40'},
            ]
        }

        # HTTP Request
        res = self.client.post(self._INGREDIENT_URL, payload, format='json')

        # Query Database
        db_data = Ingredient.objects.filter(user=self.user)
        serialized = IngredientSerializer(db_data, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Validating Response data
        self.assertEqual(
            res.data['nutrients'][0]['name'],
            payload['nutrients'][0]['name'])
        self.assertEqual(
            res.data['nutrients'][0]['grams'],
            payload['nutrients'][0]['grams'])
        self.assertEqual(
            res.data['nutrients'][1]['name'],
            payload['nutrients'][1]['name'])
        self.assertEqual(
            res.data['nutrients'][1]['grams'],
            payload['nutrients'][1]['grams'])

        # Validating Database data
        self.assertEqual(
            serialized.data[0]['nutrients'][0]['name'],
            payload['nutrients'][0]['name'])
        self.assertEqual(
            serialized.data[0]['nutrients'][0]['grams'],
            payload['nutrients'][0]['grams'])
        self.assertEqual(
            serialized.data[0]['nutrients'][1]['name'],
            payload['nutrients'][1]['name'])
        self.assertEqual(
            serialized.data[0]['nutrients'][1]['grams'],
            payload['nutrients'][1]['grams'])

    def test_update_nutrients_inside_ingredient_partiallY(self):
        """Test Updating the nutrient inside ingredient partially."""
        # Create ingredient
        ingredient = self._create_ingredient(
            user=self.user, name='Potato')
        # Create nutrient
        nutrient = self._create_nutrient(
            user=self.user, nutrient_name='Calcium', grams='2.97'
        )
        # Adding nutrient to ingredient
        ingredient.nutrients.add(nutrient)

        # payload
        payload = {
            'name': 'Tomato',
            'nutrients': [
                {'name': 'Potasium', 'grams': '2.97'},
            ]
        }
        # HTTP Request
        url = self._ingredient_detail_url(ingredient.id)
        res = self.client.patch(url, payload, format='json')

        # Query database
        db_data = Ingredient.objects.filter(
            user=self.user, id=ingredient.id
        )
        serialized = IngredientSerializer(db_data, many=True)
        slz_nutrients = serialized.data[0]['nutrients']

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], ingredient.id)
        # Validate Response data
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(
            res.data['nutrients'][0]['grams'],
            payload['nutrients'][0]['grams'])
        # Validate Database data
        self.assertEqual(res.data['nutrients'][0]['name'],
                         slz_nutrients[0]['name'])

    def test_update_nutrient_inside_ingredient_completely(self):
        """Test Update nutrient inside ingredient completely."""
        """Test Updating the nutrient inside ingredient partially."""
        # Create ingredient
        ingredient = self._create_ingredient(
            user=self.user, name='Potato')
        # Create nutrient
        nutrient = self._create_nutrient(
            user=self.user, nutrient_name='Calcium', grams='2.97'
        )
        # Adding nutrient to ingredient
        ingredient.nutrients.add(nutrient)

        # payload
        payload = {
            'name': 'Tomato',
            'nutrients': [
                {'name': 'Potasium', 'grams': '1.22'},
            ]
        }
        # HTTP Request
        url = self._ingredient_detail_url(ingredient.id)
        res = self.client.put(url, payload, format='json')

        # Query database
        db_data = Ingredient.objects.filter(
            user=self.user, id=ingredient.id
        )
        serialized = IngredientSerializer(db_data, many=True)
        slz_nutrients = serialized.data[0]['nutrients']

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], ingredient.id)
        # Validate Response data
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(
            res.data['nutrients'][0]['grams'],
            payload['nutrients'][0]['grams'])
        # Validate Database data
        self.assertEqual(
            res.data['nutrients'][0]['name'],
            slz_nutrients[0]['name'])

    def test_delete_ingredient_with_nutrient(self):
        """Test successfully deleting ingredient which had nutrient with it."""
        # Create ingredient
        ingredient = self._create_ingredient(user=self.user, name='Potato')
        # Create nutrient
        nutrient = self._create_nutrient(user=self.user,
                                         nutrient_name='Calcium',
                                         grams='2.99')
        # Adding nutrient to ingredient
        ingredient.nutrients.add(nutrient)

        # HTTP Request
        url = self._ingredient_detail_url(ingredient.id)
        res = self.client.delete(url)

        # Query Database
        db_data = Ingredient.objects.filter(
            user=self.user,
            id=ingredient.id
        )
        nutri_db_data = Nutrient.objects.filter(
            user=self.user,
            id=nutrient.id
        )

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(db_data.exists())
        self.assertTrue(nutri_db_data.exists())

    def test_delete_ingredient_and_nutrient_post_creation(self):
        """Test deleting ingredient and nutrient after creating
        it through API. We need to make sure that nutrient is
        deleted if we delete ingredient if both are created at
        the same time."""
        # Payload
        payload = {
            'name': 'Potato',
            'nutrients': [
                {'name': 'Calcium', 'grams': '1.99'}
            ]
        }

        # Creating ingredient and nutrient
        res = self.client.post(self._INGREDIENT_URL, payload, format='json')

        # Parsing data
        data = res.data
        ingre_id = data['id']
        ingre_name = data['name']
        nutri_name = data['nutrients'][0]['name']
        nutri_grams = data['nutrients'][0]['grams']

        # Assertions to find if Ingredients and Nutrients
        # were created.
        self.assertEqual(ingre_name, payload['name'])
        self.assertEqual(nutri_name, payload['nutrients'][0]['name'])
        self.assertEqual(nutri_grams, payload['nutrients'][0]['grams'])

        # Delete Ingredient
        url = self._ingredient_detail_url(ingre_id)
        res = self.client.delete(url)

        # Query Database
        db_data = Ingredient.objects.filter(
            user=self.user, id=ingre_id
        )
        nutri_db_data = Ingredient.objects.filter(
            user=self.user, id=ingre_id
        )
        # Assertions
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(db_data.exists())
        self.assertFalse(nutri_db_data.exists())
