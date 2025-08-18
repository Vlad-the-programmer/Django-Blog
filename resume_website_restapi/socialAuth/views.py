from django.contrib.auth import get_user_model

from rest_framework.reverse import reverse_lazy

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


Profile = get_user_model()

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = reverse_lazy("posts:post-list")
    client_class = OAuth2Client


