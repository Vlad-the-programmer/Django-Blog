from django.contrib.auth.tokens import default_token_generator
# DRF
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from users.models import Profile
from .models import Post


class PostApiTestCase(APITestCase):
    
    def setUp(self) -> None:
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
        print(Profile.objects.all())
        print(self.user.check_password("student123"))
        # Login user
        login_data = {"email": "vlad2@gmail.com", "password": "student123"}
        
        get_token = self.client.post(reverse('users:token_obtain_pair'), login_data)
        print('Token1 ', get_token.data)
        # Token 
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.post_create = reverse('posts:post-create')
        self.post_list = reverse('posts:posts-list')
        
        
        self.post_create_data = {
                                    "title": "django",
                                    "content": "django",
                                    "status": "publish",
                                    "add_tags":  [
                                            "Python",
                                            "Django"
                                        ],
                                    "add_category": "tests"

                            }
        
        
        self.headers = {'Authorization': 'Bearer ' + self.token.key}
        # Create a post
        self.test_post_create()
        # Kwargs for the urls
        kwargs = {'post_slug': Post.objects.first().slug}
        self.post_update_delete = reverse('posts:post-update-delete',
                                          kwargs=kwargs)
        self.post_retrieve = reverse('posts:post-retrieve', 
                                     kwargs=kwargs)
        
        return super().setUp()


    def test_post_create(self):
        response = self.client.post(self.post_create,
                                    self.post_create_data,
                                    headers=self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["slug"], self.post_create_data["title"])
        
        
    def test_posts_list(self):
        response = self.client.get(self.post_list)
        
        self.assertEqual(Post.objects.all().count(), 1)
        
        
    def test_post_update(self):
        data = {**self.post_create_data, 'title': 'django1'}
        response = self.client.post(self.post_update_delete, data, self.headers)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slug'], data['title'])
        
        
    def test_destroy_post(self):
        response = self.client.delete(self.post_update_delete, self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_retrieve_post(self):
        response = self.client.get(self.post_retrieve)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        