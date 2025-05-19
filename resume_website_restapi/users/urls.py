from django.urls import path
from dj_rest_auth import views as dj_rest_auth_views
# DRF
from rest_framework_simplejwt.views import (
                                             TokenObtainPairView,
                                             TokenRefreshView,
                                        )

from . import views as custom_views


app_name='users'

urlpatterns = [
     # Get a list of all users
     path('all-users/', custom_views.UsersListApiView.as_view(),
          name='all-users'),
     
     # Custom register and activate account views
     path('registration/', custom_views.UserSignUpApiView.as_view(),
          name='register'),
     
     path('activate/<uuid>/<token>/', custom_views.activate_account,
          name='activate'),
     
     # Custom password reset and change views
     path('password/reset/', 
          custom_views.reset_password,
          name='password_reset'),
     
     path('password/change/<uuid>/<token>/', 
          custom_views.PasswordChangeApiView.as_view(),
          name='password_change',
     ),
     
     # dj-rest-auth views
     path('dj-rest-auth/login/', 
          dj_rest_auth_views.LoginView.as_view(
                  authentication_classes = (),
               ), name='login'),
     
     path('dj-rest-auth/logout/',  
          dj_rest_auth_views.LogoutView.as_view(),
          name='logout'),

     # token obtain views
     path('token/', TokenObtainPairView.as_view(), 
          name='token_obtain_pair'),
     
     path('token/refresh/', TokenRefreshView.as_view(), 
         name='token_refresh'),
    
     # Custom views for profile detail update delete views
     path('profile/<uuid:pk>/', 
         custom_views.ProfileDetailUpdateDeleteApiView.as_view(), 
         name='profile-detail'),

     # SocialAccount auth
     path('dj-rest-auth/github/', custom_views.GitHubLogin.as_view(),
          name='github_login'),
     
     path('dj-rest-auth/google/', custom_views.GoogleLogin.as_view(), 
          name='google_login'),

     path('dj-rest-auth/facebook/', custom_views.FacebookLogin.as_view(),
          name='fb_login'),
     
     path('google/auth/', custom_views.get_google_auth_code,
          name='google_auth'),
     path('github/auth/', custom_views.get_github_auth_code,
          name='github_auth'),
]
