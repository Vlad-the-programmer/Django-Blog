from django.urls import path, include, re_path
from dj_rest_auth.registration.views import ResendEmailVerificationView
from dj_rest_auth.views import PasswordResetConfirmView
from .views import CustomRegisterView, GoogleLogin, VerifyEmailView

app_name = 'dj_rest_auth'

urlpatterns = [
    # Authentication URLs
    path('dj_rest_auth/', include('dj_rest_auth.urls')),
    
    # Registration and email verification endpoints
    path('dj_rest_auth/registration/', include([
        path('', CustomRegisterView.as_view(), name='rest_register'),
        path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
        path('verify-email/confirm/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email-confirm'),
        path('resend-email/', ResendEmailVerificationView.as_view(), name='resend-email'),
    ])),
    
    # Social authentication
    path('dj_rest_auth/google/', GoogleLogin.as_view(), name='google_login'),
    
    # Password reset endpoints
    path('password/reset/confirm/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
]

