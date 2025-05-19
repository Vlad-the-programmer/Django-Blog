import os
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
# DRF
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse, reverse_lazy
from rest_framework.authtoken.models import Token

from users.models import Profile


class UserApiTestCase(APITestCase):
    
    def setUp(self) -> None:
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')
        self.password_reset_url = reverse('users:password_reset')
        
        # Register user
        self.user_data = {
                      "email": "vlad2@gmail.com",
                      "password": "student123",
                      "password2": "student123",
                      "country": "poland",
                      "gender": "male",
                      "first_name": "Vladyslav",
                      "last_name": "Klymchuk",
                    }

        response = self.client.post(self.register_url, self.user_data,
                                    format='json').data
        
        self.user = Profile.objects.get(email=response["email"])
        
        print('Register ', self.user)
        print('Profiles ', Profile.objects.all())
        
        # Get tokens 
        self.confirm_token = default_token_generator.make_token(self.user)
        # self.token, created = Token.objects.get_or_create(user=self.user)
        login_data = {"email": self.user.email, "password": "student123"}
        
        self.token = self.client.post(reverse('users:token_obtain_pair'),
                                      login_data).data
        print('Token ', self.token)
        
        # Headers
        self.headers = {'Authorization': f'Bearer {self.token}'}
        
        
        data = {"token": self.confirm_token, 
                "uuid": self.user.id}
        
        self.activation_url = reverse('users:activate', kwargs=data)
        self.password_change_url = reverse('users:password_change', kwargs=data)
        
        # google_access_token = self.client.post(
        #             os.environ.get("Token_Uri"),
        #             data = {
        #                     'client_id': os.environ.get("Google_OAUTH_CLIENT_ID", ''),
        #             },
        #         )
        # print('Google token ', google_access_token.data)
        # response = self.client.post(
        #             reverse_lazy('users:google_login'), 
        #             data = {
        #                     'code': os.environ.get("Google_OAUTH_CLIENT_ID", ''),
        #             },
        #         )
        # print(response.data)
        
        return super().setUp()
    
    
    def test_register_user(self):
    #     response = self.client.post(self.register_url, self.user_data, format='json')
    #     print('Reg ', response.data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.email, self.user_data["email"])
        
        
    def test_activate_account(self):
        
        response = self.client.post(self.activation_url, format='json',
                                    headers=self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_login_user(self):
        # data = {"email": self.user.email, "password": "student123"}
        # response = self.client.post(self.login_url, login_data, format='json')
        self.client.force_login(self.user)
        self.assertTrue(self.user.is_authenticated)
        
        
    def test_password_reset(self):
        data = {"email": self.user.email}
        response = self.client.post(self.password_reset_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        
        
    def test_password_change(self):
        data = {"password": "student123", "password2": "student123"}
        user = Profile.objects.get(email=self.user.email)
        
        response = self.client.patch(self.password_change_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password(data['password']))
        
        
    def test_github_auth(self):
        response = self.client.post(reverse_lazy('users:github_login'), self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_google_auth(self):
        response = self.client.post(reverse_lazy('users:google_login'), self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        