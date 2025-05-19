from django.urls import path
from allauth.account import views as account

from . import views
from .forms import UserLoginForm


app_name='users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', account.LoginView.as_view(
                                               form_class=UserLoginForm,
                                            ), name='login'),
    path('logout/', account.LogoutView.as_view(), name='logout'),
    path('profile/detail/<int:pk>/', views.ProfileDetail.as_view(),
                                                        name='profile-detail'),
    path('profile/delete/<int:pk>/', views.ProfileDelete.as_view(),
                                                        name='profile-delete'),
    path('profile/update/<int:pk>/', views.ProfileUpdate.as_view(),
                                                        name='profile-update'),
    
    path('forgot-password/', views.forgotPassword, name='forgotPassword'),
    path('reset-password-validate/<int:pk>', views.reset_password_validate,
         name='reset-password-validate'),
    path('reset-password/<int:pk>', views.resetPassword, name='resetPassword'),
    
    
]