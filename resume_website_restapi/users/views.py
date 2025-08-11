import logging
import os
from typing import Any, Dict, Optional

import requests
from django.db.models import Q
from django.urls import reverse_lazy
# Django
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, logout, update_session_auth_hash
from django.conf import settings

# Django REST Framework
from rest_framework import status, permissions, generics, serializers
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView

# DRF Spectacular
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes

# Social Auth
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

# Local
from . import exceptions as custom_exceptions
from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    PasswordResetSerializer,
    ChangePasswordSerializer,
)

# Logging
logger = logging.getLogger(__name__)

# Get user model
Profile = get_user_model()


@extend_schema(
    tags=['Authentication'],
    request=UserRegisterSerializer,
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description='User registered successfully. Verification email sent.'
        ),
        400: OpenApiResponse(description='Invalid input data')
    },
    examples=[
        OpenApiExample(
            'Registration Example',
            value={
                'email': 'user@example.com',
                'username': 'newuser',
                'password': 'SecurePass123!',
                'password2': 'SecurePass123!',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            request_only=True
        )
    ]
)
class UserSignUpApiView(generics.CreateAPIView):
    """
    Register a new user account.
    
    Creates a new user and sends a verification email to the provided email address.
    The user account will be inactive until the email is verified.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    
    def create(self, request: Request, *args, **kwargs) -> Response:
        """Handle user registration with email verification."""
        try:
            serializer = self.get_serializer(
                data=request.data, 
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            logger.info(
                f"New user registered: {serializer.data.get('email')}. "
                "Verification email sent."
            )
            
            # Don't return the password hash in the response
            response_data = {
                'detail': _('Registration successful. Please check your email to verify your account.'),
                'email': serializer.data.get('email'),
                'username': serializer.data.get('username')
            }
            
            return Response(
                response_data,
                status=status.HTTP_201_CREATED,
                headers=self.get_success_headers(serializer.data)
            )
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            raise


        
@extend_schema(
    tags=['Users'],
    parameters=[
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search users by username, first name, or last name',
            required=False
        )
    ],
    responses={
        200: UserSerializer(many=True),
        403: OpenApiResponse(description='Forbidden')
    }
)
class UsersListApiView(generics.ListAPIView):
    """
    List all users in the system.
    
    Only accessible by admin users. Supports searching by username, first name, or last name.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering_fields = ('date_joined', 'last_login', 'username')
    
    def get_queryset(self):
        """Return the list of users with optional search filtering."""
        queryset = Profile.objects.select_related(
            # Add any OneToOne or ForeignKey relationships here
        ).prefetch_related(
            'groups',
            'user_permissions',
            # Add other ManyToMany or reverse relationships as needed
        )
        
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
            
        return queryset.order_by('-date_joined').only(
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'last_login', 'is_active', 'is_staff'
        )


@extend_schema(
    tags=['Authentication'],
    parameters=[
        OpenApiParameter(
            name='uuid',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='User ID for account activation'
        ),
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Activation token'
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Account activated successfully',
            examples={
                'application/json': {
                    'detail': 'Account activated successfully. You can now log in.'
                }
            }
        ),
        400: OpenApiResponse(
            description='Invalid activation link',
            examples={
                'application/json': {
                    'error': 'Invalid or expired activation link.'
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def activate_account(request: Request, uuid: str, token: str) -> Response:
    """
    Activate a user account using the provided UUID and token.
    
    This endpoint is accessed when a user clicks the activation link in their email.
    """
    try:
        user = Profile.objects.get(id=uuid, is_active=False)
    except (Profile.DoesNotExist, TypeError, ValueError, OverflowError):
        logger.warning(f"Invalid activation attempt for UUID: {uuid}")
        return Response(
            {'error': _('Invalid or expired activation link.')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        logger.info(f"User {user.get_username()} account activated successfully.")
        
        return Response(
            {'detail': _('Account activated successfully. You can now log in.')},
            status=status.HTTP_200_OK
        )
    
    logger.warning(f"Invalid activation token for user: {user.email}")
    return Response(
        {'error': _('Invalid or expired activation link.')},
        status=status.HTTP_400_BAD_REQUEST
    )


@extend_schema(
    tags=['Authentication'],
    request=inline_serializer(
        name='PasswordResetRequest',
        fields={
            'email': serializers.EmailField(help_text='Email address for password reset')
        }
    ),
    responses={
        200: OpenApiResponse(
            description='Password reset email sent if account exists',
            examples={
                'application/json': {
                    'detail': 'If an account exists with this email, you will receive a password reset link.'
                }
            }
        ),
        400: OpenApiResponse(description='Invalid input data')
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request: Request) -> Response:
    """
    Request a password reset email.
    
    Sends a password reset email to the provided email address if an account exists.
    For security reasons, this endpoint always returns a 200 status code, even if the 
    email doesn't exist in our system.
    """
    try:
        serializer = PasswordResetSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        logger.info(f"Password reset requested for email: {request.data.get('email')}")
        
        return Response(
            {
                'detail': _(
                    'If an account exists with this email, you will receive a password reset link.'
                )
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}", exc_info=True)
        # Still return success to prevent email enumeration
        return Response(
            {'detail': _('If an account exists, you will receive a password reset link.')},
            status=status.HTTP_200_OK
        )


@extend_schema(
    tags=['Authentication'],
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(
            description='Password changed successfully',
            examples={
                'application/json': {
                    'detail': 'Password updated successfully.'
                }
            }
        ),
        400: OpenApiResponse(description='Invalid input data'),
        401: OpenApiResponse(description='Authentication credentials were not provided'),
    }
)
class PasswordChangeApiView(generics.UpdateAPIView):
    """
    Change user password.
    
    Allows an authenticated user to change their password. Requires the current password 
    and the new password (with confirmation).
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        """Return the current user."""
        return self.request.user
    

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
        
        update_session_auth_hash(request, user)
        return Response(
            {'detail':'Password changed!'},
            status=status.HTTP_200_OK,
        )
        
        
class ProfileDetailUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user profile.
    """
    serializer_class = UserSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    
    def get_queryset(self):
        """Optimize the queryset with select_related and prefetch_related."""
        return Profile.objects.select_related(
            # Add any OneToOne or ForeignKey relationships here
        ).prefetch_related(
            'groups',
            'user_permissions',
            # Add other ManyToMany or reverse relationships as needed
        ).only(
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'last_login', 'is_active', 'is_staff',
            'bio', 'profile_picture', 'date_of_birth', 'gender',
            'phone_number', 'address', 'city', 'country', 'postal_code'
        )
    
    def get_object(self):
        """Retrieve and return the authenticated user's profile."""
        try:
            return self.get_queryset().get(id=self.kwargs.get('pk'))
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist")
    
    def destroy(self, request, *args, **kwargs):
        """Delete the user profile."""
        profile = self.get_object()
        self.perform_destroy(profile)
        logout(request)
        return Response(
            {'detail': 'Profile deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT,
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
    
    
@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([])
def get_github_auth_code(request):
    auth_code = requests.get()
    print(request.GET)
    # print("Code ", auth_code.text)
    
    code = "4%2F0AWgavddUzTJER6UeNDCsYCBxL9dEtywFw-nFsPt_l94igeorg_E_h-TeNtGeryg0JBBnaQ"
    access_token = requests.post(f"https://oauth2.googleapis.com/token?code={code}&client_id=364189943403-pguvlcnjp1kd9p8s1n5kruhboa3sj8fq.apps.googleusercontent.com&client_secret=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&redirect_uri=http://127.0.0.1:8001/posts/&grant_type=authorization_code")
    print("Token ", access_token.json)
    
    return Response({
                        "code": auth_code.text,
                        # "token": access_token.request.body,
                    },status=status.HTTP_200_OK)