"""
Tests for testing User APIs
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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
        """Test case to raise error that password length is less
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

    def test_create_token_for_valid_credentials(self):
        """Test token is created successfully when user passed
        correct credentials."""
        user_details = {
            'email': 'test@example.com',
            'password': 'TestPass123',
            'name': 'Test Name'
        }
        # Create user directly in db
        create_user(**user_details)

        # Create Token with HTTP Request
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_token_creation_fails_with_invalid_credentials(self):
        """Test Token creation request fails when user inputs
        incorrect credentials."""
        user_details = {
            'email': 'test@example.com',
            'password': 'TestPass123',
            'name': 'Test Name'
        }
        # Create user directly in db
        create_user(**user_details)

        # Try to create token with HTTP Request
        payload = {
            'email': user_details['email'],
            'password': 'TestFailPassword',
        }
        res = self.client.post(TOKEN_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_creation_fails_with_blank_password(self):
        """Test token creation request will fail if the user inputs
        blank email or password"""
        user_details = {
            'email': 'test@example.com',
            'password': 'TestPass123',
        }
        # Create user directly in db
        create_user(**user_details)

        # Try to create token with HTTP Request
        payload = {
            'email': user_details['email'],
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrieve_data_failing_with_unauthorized_user(self):
        """Test retrieving data failure when accessed unauthorized."""
        # HTTP GET Request on 'ME_URL' Endpoint
        res = self.client.get(ME_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test case for authorized user."""
    def setUp(self):
        """Setting up environment for authorized test cases."""
        # Creating user directly in db
        user_creds = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'SuccessPassword123'
        }
        self.user = create_user(**user_creds)

        # Instantiating APIClient
        self.client = APIClient()

        # Authenticating user
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_details_success(self):
        """Retrieve user data successfully"""
        res = self.client.get(ME_URL)

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': 'Test Name',
            'email': 'test@example.com'
        })

    def test_post_method_not_allowed(self):
        """Test 'POST' method not allowed on 'ME_URL' Endpoint."""
        res = self.client.post(ME_URL)

        # Assetions
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updating_user_data_success(self):
        """Test successfully updating user data with 'PATCH' method."""
        payload = {
            'name': 'Updated Name',
            'password': 'NewPass123'
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
