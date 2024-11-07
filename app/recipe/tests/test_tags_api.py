"""
# app/recipe/tests/test_tags_api.py
Test for the tags APIs.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from ..serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


def tag_detail_url(tag_id: int) -> str:
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email, password):
    """Create user directly into the db."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_tag(user, tag_name):
    """Create tag and assoicate it with the user."""
    return Tag.objects.create(user=user, name=tag_name)


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


class PublicTagAPITests(TestCase):
    """Test case for unauthenticate API requests on Tags."""
    def setUp(self):
        """Setting up testing environment."""
        self.client = APIClient()

    def test_retrieve_tag_list(self):
        """Test retrieve tag lists"""
        # HTTP Request to fetch tag list
        res = self.client.get(TAG_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Test case for testing authenticated Tag API Requests."""
    def setUp(self):
        """Setting up testing environment."""
        # Create user
        self.user = create_user('test@example.com', 'testPass123')
        # Authorize user to perform HTTP Request.
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tag_list_success(self):
        """Test to successfully retrieve tag lists."""
        # Create tags and associate it with the user
        create_tag(user=self.user, tag_name='Desert')
        create_tag(user=self.user, tag_name='Lunch')

        # HTTP Request to retrieve the tags
        res = self.client.get(TAG_URL)

        # Fetch tags from db and Serializer (Convert
        # JSON Respon with DB Response)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        # Create Other User
        other_user = create_user('otherUser@example.com', 'OtherPass123')

        # Create Tags
        create_tag(user=other_user, tag_name='Breakfast')
        create_tag(user=other_user, tag_name='Lunch')
        tag = create_tag(user=self.user, tag_name='Dinner')

        # HTTP Request to retrieve tag list
        res = self.client.get(TAG_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_on_particular_tag(self):
        """Test 'PATCH' Method to update particular tag for the user."""
        # Create tag directly in db
        tag = create_tag(user=self.user, tag_name='Tomato')

        # HTTP Request
        payload = {'name': 'Potato'}
        url = tag_detail_url(tag.id)
        res = self.client.patch(url, payload, format='json')

        # Refresh db for the tag
        tag.refresh_from_db()

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test Deleting a tag."""
        # Create a tag
        tag = create_tag(self.user, 'Sugar')

        # HTTP Request
        url = tag_detail_url(tag.id)
        res = self.client.delete(url)

        # Fetch data from db
        tag_db_data = Tag.objects.filter(user=self.user)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(tag_db_data.exists())

    def test_filter_tags_assigned_to_recipe(self):
        """Test filtering tags which are assiged to recipe."""
        # Create tags
        tag1 = create_tag(user=self.user, tag_name='Breakfast')
        tag2 = create_tag(user=self.user, tag_name='Lunch')

        # Create recipe
        recipe = create_recipe(user=self.user, title='Egg Toast')

        # Adding tag to recipe
        recipe.tags.add(tag1)

        # HTTP Request
        res = self.client.get(TAG_URL, {'assigned_only': 1})

        # Serialize Data
        serialized_tag1 = TagSerializer(tag1)
        serialized_tag2 = TagSerializer(tag2)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serialized_tag1.data, res.data)
        self.assertNotIn(serialized_tag2.data, res.data)

    def test_filter_tag_return_unique(self):
        """Test filter tags to return unique list of tags."""
        tag = create_tag(user=self.user, tag_name='Breakfast')
        create_tag(user=self.user, tag_name='Lunch')

        recipe1 = create_recipe(user=self.user, title='Pasta')
        recipe2 = create_recipe(user=self.user, title='Idle')

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
