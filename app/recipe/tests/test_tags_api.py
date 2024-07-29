"""
# app/recipe/tests/test_tags_api.py
Test for the tags APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from ..serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')

def tag_detail_url(tag_id):
    return reverse('recipe:tag-details', args=[tag_id])


def create_user(email, password):
    """Create user directly into the db."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_tag(user, tag_name):
    """Create tag and assoicate it with the user."""
    return Tag.objects.create(user=user, name=tag_name)


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
