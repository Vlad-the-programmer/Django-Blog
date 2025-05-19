from django.test import TestCase
from django.urls import reverse, reverse_lazy


from .models import Profile

class UserTestCase(TestCase):
    
    def setUp(self):
        
        # Register user
        self.user_data = {
                      "email": "vlad2@gmail.com",
                      "password": "student123",
                      "country": "poland",
                      "gender": "male",
                      "first_name": "Vladyslav",
                      "last_name": "Klymchuk",
                    }


        self.user = Profile.objects.create_user(**self.user_data)
        print(self.user.username)
            
        # Urls
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')
        self.password_reset_email_confirm = reverse('users:forgotPassword')
        self.password_reset_url = reverse('users:resetPassword', 
                                          kwargs={'pk': self.user.pk})
        self.update_profile_url = reverse_lazy('users:profile-update', 
                                          kwargs={'pk': self.user.pk})
        
        
    def test_user_registered(self):
        self.assertEqual(Profile.objects.all().count(), 1)
        self.assertEqual(self.user.username, 'vlad2')
        
    
    def test_login_user(self):
        login_data = {"email": self.user_data['email'],
                      'password': self.user_data['password'],
                    }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEquals(True, self.user.is_authenticated)
        
        
        
    def test_password_change(self):
        data = {"password": self.user_data['password'],
                "password2": self.user_data['password']}
        
        user = Profile.objects.get(email=self.user_data['email'])
        
        response = self.client.patch(self.password_reset_url, 
                                     data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.check_password(data['password']))
        
        
    def test_profile_update(self):
        data = {'username': 'test', 'first_name': 'vlad'}
        response = self.client.patch(self.update_profile_url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(True, self.user.is_authenticated)
        self.assertEqual(self.user.username, data['username'])
        
        # self.assertEqual(Profile.objects.get(username='test').first_name, 
        #                                     data['first_name'])
        
    
    # def test_password_reset_confirm(self):
    #     data = {"email": self.user.email}
    #     response = self.client.post(self.password_reset_email_confirm, data)
        
    #     self.assertEqual(response.status_code, 302)