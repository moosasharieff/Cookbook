"""
Tests for testing User APIs
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')

def create_user(**params):
    """Creates users directly into the database"""
    return get_user_model().objects.create_user(**params)

class PublicUserAPITestClass(TestCase):
    def setUp(self):
        """Setting up this class to perform API tests."""
        self.client = APIClient()

    def test_create_user_success(self):
        """Tests user is created successfully."""
        # Payload for HTTP Requests
        payload = {
            'email': 'test@example.com',
            'password': 'testPassword123',
            'name': 'Test Name'
        }

        # HTTP POST Request to create user
        res = self.client.post(path=CREATE_USER_URL, data=payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Asserting for email & password
        # Fetches data from db
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(user.email, payload['email'])
        self.assertTrue(user.check_password(payload['password']))


        # Asserting to check password in not present in response data
        self.assertNotIn('password', res.data)

    def test_user_email_already_exits(self):
        """Test to confirm if user email already exists in database."""
        # Payload for HTTP Requests
        payload = {
            'email': 'test@example.com',
            'password': 'testPassword123',
            'name': 'Test Name'
        }

        # Creating user directly into db
        create_user(**payload)
        # HTTP POST Request to create user
        res = self.client.post(path=CREATE_USER_URL, data=payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_length_too_short_error(self):
        """Test case to raise error that password lenght is less
        than 5 characters."""
        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'Test Name'
        }

        # HTTP POST Request to create user
        res = self.client.post(path=CREATE_USER_URL, data=payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Checks if user was created with less password characters
        user_exists = get_user_model().objects.filter(email=payload['email'])
        self.assertFalse(user_exists)

