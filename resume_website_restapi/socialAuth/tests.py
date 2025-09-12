from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken


Profile = get_user_model()


class SocialAuthTestCase(APITestCase):
    """Test cases for social authentication endpoints."""

    def setUp(self):
        """Set up test data and URLs."""
        # URLs
        self.register_url = reverse('dj_rest_auth:register')
        self.login_url = reverse('dj_rest_auth:login')
        self.logout_url = reverse('dj_rest_auth:logout')
        self.password_reset_url = reverse('dj_rest_auth:password_reset')
        self.password_change_url = reverse('users:password_change')
        self.github_login_url = reverse('users:github_login')
        self.google_login_url = reverse('users:google_login')

        # Test user data
        self.user_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!",
            "country": "US",
            "gender": "male",
            "first_name": "Test",
            "last_name": "User",
        }

        # Create test user
        self.user = Profile.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            country=self.user_data['country'],
            gender=self.user_data['gender'],
            is_active=True
        )

        # Get JWT tokens
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

        # Set up client with authentication
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Generate activation token
        self.activation_token = default_token_generator.make_token(self.user)
        self.activation_url = reverse('users:activate', kwargs={
            'token': self.activation_token,
            'uuid': self.user.id
        })

    def test_register_user_success(self):
        """Test successful user registration."""
        new_user_data = {
            "email": "newuser@example.com",
            "password": "NewPass123!",
            "password2": "NewPass123!",
            "country": "CA",
            "gender": "female",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(self.register_url, new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], new_user_data['email'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_register_duplicate_email(self):
        """Test registration with duplicate email fails."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_activate_account_success(self):
        """Test account activation with valid token."""
        response = self.client.post(self.activation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_account_invalid_token(self):
        """Test account activation with invalid token."""
        invalid_activation_url = reverse('users:activate', kwargs={
            'token': 'invalid-token',
            'uuid': self.user.id
        })
        response = self.client.post(invalid_activation_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Test successful user login."""
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "email": self.user_data['email'],
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        """Test user logout."""
        response = self.client.post(self.logout_url, {"refresh": self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset(self):
        """Test password reset request."""
        data = {"email": self.user.email}
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(self.password_reset_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_change(self):
        """Test password change."""
        new_password = "NewSecurePass123!"
        data = {
            "old_password": self.user_data['password'],
            "new_password1": new_password,
            "new_password2": new_password
        }
        response = self.client.post(self.password_change_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    @patch('social_core.backends.oauth.BaseOAuth2.auth_complete')
    def test_github_auth_success(self, mock_auth_complete):
        """Test successful GitHub OAuth authentication."""
        mock_auth_complete.return_value = {
            'email': 'github@example.com',
            'first_name': 'GitHub',
            'last_name': 'User',
            'access_token': 'github-token-123'
        }

        response = self.client.post(self.github_login_url, {"code": "github-auth-code"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    @patch('social_core.backends.oauth.BaseOAuth2.auth_complete')
    def test_google_auth_success(self, mock_auth_complete):
        """Test successful Google OAuth authentication."""
        mock_auth_complete.return_value = {
            'email': 'google@example.com',
            'first_name': 'Google',
            'last_name': 'User',
            'access_token': 'google-token-123'
        }

        response = self.client.post(self.google_login_url, {"code": "google-auth-code"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_refresh_token(self):
        """Test token refresh."""
        refresh_url = reverse('users:token_refresh')
        data = {"refresh": self.refresh_token}
        response = self.client.post(refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_protected_endpoint_access(self):
        """Test access to protected endpoint with valid token."""
        response = self.client.get(reverse('user-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_protected_endpoint_unauthorized(self):
        """Test access to protected endpoint without token."""
        self.client.credentials()  # Clear credentials
        response = self.client.get(reverse('user-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)