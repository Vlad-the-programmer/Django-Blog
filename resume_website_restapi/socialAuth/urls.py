from dj_rest_auth.registration.views import VerifyEmailView
from django.urls import path, include
from .views import GoogleLogin


urlpatterns = [
    path('dj_rest_auth/', include('dj_rest_auth.urls')),
    path('dj_rest_auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj_rest_auth/google/', GoogleLogin.as_view(), name='google_login'),

    path('dj-rest-auth/account-confirm-email/', VerifyEmailView. as_view(),
         name='account_email_verification_sent'),

]

