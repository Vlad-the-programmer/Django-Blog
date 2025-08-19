from dj_rest_auth.registration.views import VerifyEmailView
from django.urls import path, include, re_path
from .views import GoogleLogin

app_name = 'dj_rest_auth'

urlpatterns = [
    path('dj_rest_auth/', include('dj_rest_auth.urls')),
    path('dj_rest_auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj_rest_auth/google/', GoogleLogin.as_view(), name='google_login'),

    re_path(
        r'^account-confirm-email/(?P<key>[-:\w]+)/$',
        VerifyEmailView.as_view(),
        name='account_confirm_email',
    ),

]

