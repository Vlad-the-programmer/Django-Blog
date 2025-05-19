# DRF
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Category
from users.models import Profile


class CategoryTestCase(APITestCase):
    
    def setUp(self):
        # Register user
        self.register_url = reverse('users:register')
        
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
        
        # Getting user
        self.user = Profile.objects.get(email=response["email"])
        # Login user
        login_data = {"email": "vlad2@gmail.com", "password": "student123"}
        
        get_token = self.client.post(reverse('users:token_obtain_pair'), login_data)

        print(Profile.objects.all())
        print('Token1 ', get_token.data)
        # Token 
        self.token, created = Token.objects.get_or_create(user=self.user)
        # Creating a category
        url = reverse('category:category-create')
        self.data = {'title': 'image'}
        
        response2 = self.client.post(url, self.data, format='json',
                                    headers={'Authorization': 'Bearer ' \
                                                    + self.token.key})
        
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        return super().setUp()
    
    
    def test_create_category(self):
       
        self.assertEqual(Category.objects.get(title=self.data['title']).title, 
                         self.data['title'])
        
        
    def test_category_posts_list(self):
        url_data = {'category_slug': 'image'}
        
        url = reverse('category:category-posts', kwargs=url_data)
        response = self.client.get(url, format='json',
                                   headers={'Authorization': 'Bearer ' \
                                                + self.token.key})
        
        # self.assertEqual(len(response.data), Category.objects.count())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_category_update(self):
        url_data = {'category_slug': 'image'}
        url = reverse('category:category-update-delete', kwargs=url_data)
        
        data = {'title': 'image1', 'slug': 'image1'}
        
        response = self.client.put(url, data, format='json',
                                   headers={'Authorization': 'Bearer ' \
                                                + self.token.key})
        
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['slug'], data['slug'])
        
        
    def test_category_retrieve(self):
        url_data = {'category_slug': 'image'}
        url = reverse('category:category-retrieve', kwargs=url_data)
        
        response = self.client.get(url, format='json')
        print('Retreive ',response)
        
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'],
                         Category.objects.get(slug=url_data['category_slug']).title)
        
        
    def test_category_delete(self):
        url_data = {'category_slug': 'image'}
        url = reverse('category:category-update-delete', kwargs=url_data)
        
        response = self.client.delete(url,
                                      headers={'Authorization': 'Bearer ' \
                                                + self.token.key})
        print('Category-delete', response)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        
    