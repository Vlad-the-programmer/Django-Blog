import requests
import os
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
# Auth
from django.contrib.auth import get_user_model, logout
from allauth.account.utils import logout_on_password_change
# SocialAccount auth
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

# REST FRAMEWORK 
from rest_framework.reverse import reverse, reverse_lazy
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import (
                                            api_view, 
                                            permission_classes, 
                                            authentication_classes,
                                    )
from rest_framework import generics

from .serializers import (
                        UserRegisterSerializer, 
                        UserSerializer, 
                        PasswordResetSerializer,
                        ChangePasswordSerializer,
                    )

from . import exceptions as custom_exceptions


Profile = get_user_model()


class UserSignUpApiView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


        
class UsersListApiView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = Profile.objects.all()


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny,])
def activate_account(request, uuid, token):
    try:
        user = Profile.objects.get(id=uuid)
    except (Profile.DoesNotExist, TypeError, ValueError, OverflowError):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
    else:
        raise custom_exceptions.UserOrTokenNotValid
    
    return Response(
        {"detail: Activated"},
        status=status.HTTP_200_OK,
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def reset_password(request, *args, **kwargs):
    print('kwargs', kwargs)
    serializer = PasswordResetSerializer(
            data=request.data, 
            context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    
    return Response(
        {"detail": "Sent an confirmation email"},
        status=status.HTTP_302_FOUND,
    )
    

class PasswordChangeApiView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.AllowAny,)
    
    
    def get_object(self):
        try:
            profile = Profile.objects.get(id=self.kwargs.get('uuid', ''))
        except Profile.DoesNotExist:
            profile = None
        
        return profile 
    

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(
                                            instance=user,
                                            data=request.data,
                                            partial=True,
                                            context={'request': self.request},
                                        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logout_on_password_change(request, user)
        return Response(
            {'detail':'Password changed!'},
            status=status.HTTP_200_OK,
        )
        
        
class  ProfileDetailUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    
    
    def get_object(self):
        try:
            profile = Profile.objects.get(id=self.kwargs.get('pk', ''))
        except Profile.DoesNotExist:
            profile = None
        print(self.request.user, self.request.user.is_authenticated)
        print(self.request.user.auth_token)
        
        return profile 
    
    
    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile is not None:
            self.perform_destroy(profile)
            logout(request)
            return Response(
                {'detail': 'Profile deleted!'},
                status=status.HTTP_200_OK,
            )
            
        return Response(
                        {'detail': 'Profile does not exist!'},
                        status=status.HTTP_200_OK,
                    )
      

# the Logout dj-rest-auth view and this one do not work   
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, ])
def logout_user(request):

    request.user.auth_token.delete()

    logout(request)

    return Response('User Logged out successfully')


# Social account auth

class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = reverse_lazy('posts:posts-list')
    client_class = OAuth2Client


# if you want to use Authorization Code Grant, use this
class GoogleLogin(SocialLoginView): 
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:8000/accounts/google/login/callback/'
    client_class = OAuth2Client
    
    
class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    
@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([])
def get_google_auth_code(request):
    auth_code = requests.get(os.environ.get("Google_Auth_Uri"))
    print(request.GET)
    print("Code ", auth_code.text)
    
    access_token = requests.post(os.environ.get("Google_Token_Uri"))
    # print("Token ", access_token.json)
    
    return Response({
                        "code": auth_code.text,
                        "token": access_token.request.body,
                    },status=status.HTTP_200_OK)
    
    
# @api_view(["GET", "POST"])
# @authentication_classes([])
# @permission_classes([])
# def get_github_auth_code(request):
#     auth_code = requests.get()
#     print(request.GET)
#     # print("Code ", auth_code.text)
    
#     # code = "4%2F0AWgavddUzTJER6UeNDCsYCBxL9dEtywFw-nFsPt_l94igeorg_E_h-TeNtGeryg0JBBnaQ"
#     # access_token = requests.post(f"https://oauth2.googleapis.com/token?code={code}&client_id=364189943403-pguvlcnjp1kd9p8s1n5kruhboa3sj8fq.apps.googleusercontent.com&client_secret=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&redirect_uri=http://127.0.0.1:8001/posts/&grant_type=authorization_code")
#     # print("Token ", access_token.json)
    
#     return Response({
#                         "code": auth_code.text,
#                         # "token": access_token.request.body,
#                     },status=status.HTTP_200_OK)