from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')   # URL we use to make HTTP POST request
# to generate token
ME_URL = reverse('user:me')


# **param is a dynamic list of argument
def create_user(**param):
    return get_user_model().objects.create_user(**param)


# Separate Public API test and Private API test
# Public: unauthenticate. Anyone on the internet can make the request.
# Example: create user request
# Private: require authenticate. User need to be authenticated to make request
# Example: change password, update details, etc...
class PublicUserApiTests(TestCase):
    """
    Test the users API (public)
    """
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test creating user with valid payload is successful
        """
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        # Make http post request
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # We expect the object user return along with HTTP 201
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        # We check if the password is not return in data
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """
        Test creating user that already exists fails
        """
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        # Create a user with payload
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        # We expect this is bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test password must be more than 5 characters
        """
        # payload with short password
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'pw',
            'name': 'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        # Expect this is bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Expect this user does not exist
        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """
        Test that a token is created for the user
        """
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'testpass',
            'name': 'Test name'
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        # Check the token is included in response data
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Test that token is not created if invalid credentials are given
        """
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'wrong',
        }
        create_user(email=payload['email'], password='testpass')
        res = self.client.post(TOKEN_URL, payload)

        # Check token is not in response data
        self.assertNotIn('token', res.data)
        # Check this is HTTP 400 Bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that token is not created if user doesn't exist
        """
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'testpass',
        }
        res = self.client.post(TOKEN_URL, payload)

        # Check token is not in response data
        self.assertNotIn('token', res.data)
        # Check this is HTTP 400 Bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
        Test that email and password are required
        """
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        # Check token is not in response data
        self.assertNotIn('token', res.data)
        # Check this is HTTP 400 Bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Test that authentication is required for users.
        We don't want unauthenticated user to access ME_URL
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test API requests that require authentication
    """

    def setUp(self):
        self.user = create_user(
            email='test@londonappdev.com',
            password='testpass',
            name='name'
        )
        self.client = APIClient()
        # Make this user authenticated
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test retrieving profile for togged in used
        """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # We expect to see name, email in the data
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_me_not_allowed(self):
        """
        Test that POST is not allowed on the me url
        """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        Test updating the user profile for authenticated user
        """
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        # Update user with the latest value from db
        self.user.refresh_from_db()

        # Check return status 200, name and password are updated
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
