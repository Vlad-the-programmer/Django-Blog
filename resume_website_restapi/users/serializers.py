import re
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# Third-party
from django_countries.serializer_fields import CountryField

# DRF
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer

# Local
from base_utils import emails_handler
from .models import Gender
from .exceptions import NotOwner, UserAlreadyExists, InvalidPasswordFormat, WeakPasswordError

# Constants
PASSWORD_MIN_LENGTH = 8
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]+$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault('style', {})
        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True
        kwargs.setdefault('min_length', PASSWORD_MIN_LENGTH)
        super().__init__(**kwargs)
        self.validators.append(self._validate_password_strength)
    
    def _validate_password_strength(self, value):
        """Validate password strength."""
        if len(value) < PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError(
                _(f'Password must be at least {PASSWORD_MIN_LENGTH} characters long.')
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(_('Password must contain at least one digit.'))
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(_('Password must contain at least one uppercase letter.'))
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(_('Password must contain at least one lowercase letter.'))

Profile = get_user_model()


@extend_schema_serializer(
    exclude_fields=['is_staff', 'is_active'],
    examples=[
        OpenApiExample(
            'User Profile Example',
            value={
                'username': 'johndoe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'gender': 'M',
                'country': 'US',
                'featured_image': None,
                'date_joined': '2023-01-01T12:00:00Z',
                'last_login': '2023-01-01T12:00:00Z'
            },
            response_only=True
        )
    ]
)
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data.
    Used for retrieving and updating user information.
    """
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=Profile.objects.all(),
                lookup='iexact',
                message=_('A user with this email already exists.')
            )
        ],
        error_messages={
            'invalid': _('Enter a valid email address.'),
            'blank': _('This field may not be blank.')
        }
    )
    username = serializers.CharField(
        max_length=100,
        required=False,
        validators=[
            UniqueValidator(
                queryset=Profile.objects.all(),
                lookup='iexact',
                message=_('A user with this username already exists.')
            )
        ],
        error_messages={
            'max_length': _('Username cannot be longer than 100 characters.'),
            'invalid': _('Username can only contain letters, numbers, and underscores.')
        }
    )
    gender = serializers.ChoiceField(
        choices=Gender,
        allow_blank=True,
        allow_null=True,
        required=False,
        error_messages={
            'invalid_choice': _('Please select a valid gender.')
        }
    )
    country = CountryField(
        required=False,
        help_text=_('ISO 3166-1 alpha-2 country code (e.g., US, GB, DE)')
    )
    featured_image = serializers.ImageField(
        allow_empty_file=False,
        required=False,
        use_url=True,
        help_text=_('Profile picture for the user')
    )
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'gender',
            'country',
            'featured_image',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'is_staff', 'is_active', 'date_joined', 'last_login']

    def validate_username(self, value):
        """Validate username format."""
        if not USERNAME_REGEX.match(value):
            raise serializers.ValidationError(
                _('Username can only contain letters, numbers, and underscores.')
            )
        return value.lower()
    
    def validate_email(self, value):
        """Validate email format."""
        if not EMAIL_REGEX.match(value):
            raise serializers.ValidationError(_('Enter a valid email address.'))
        return value.lower()
    
    def update(self, instance, validated_data):
        """Update user profile with validated data."""
        request = self.context.get('request')
        
        if not request or instance != request.user:
            raise NotOwner(_('You do not have permission to update this profile.'))
        
        # Don't allow updating email through this endpoint
        if 'email' in validated_data and validated_data['email'] != instance.email:
            raise serializers.ValidationError({
                'email': _('Email cannot be changed through this endpoint.')
            })
        
        # Process the image if provided
        if 'featured_image' in validated_data and validated_data['featured_image'] is None:
            # If None is passed, we want to clear the image
            instance.featured_image.delete(save=False)
        
        return super().update(instance, validated_data)


@extend_schema_serializer(
    exclude_fields=['is_staff', 'is_active'],
    examples=[
        OpenApiExample(
            'Registration Example',
            value={
                'email': 'user@example.com',
                'username': 'newuser',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'SecurePass123!',
                'password2': 'SecurePass123!',
                'gender': 'M',
                'country': 'US'
            },
            request_only=True
        )
    ]
)
class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles user account creation with email verification.
    """
    password = PasswordField(
        write_only=True,
        required=True,
        help_text=_(
            'Password must be at least 8 characters long and contain at least one uppercase letter, '
            'one lowercase letter, and one number.'
        )
    )
    password2 = PasswordField(
        write_only=True,
        required=True,
        help_text=_('Enter the same password as above for verification.')
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=Profile.objects.all(),
                message=_('A user with this email already exists.')
            )
        ]
    )
    username = serializers.CharField(
        max_length=100,
        required=True,
        validators=[
            UniqueValidator(
                queryset=Profile.objects.all(),
                message=_('A user with this username already exists.')
            )
        ]
    )
    country = CountryField(required=False)

    class Meta:
        model = Profile
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'gender',
            'country',
            'featured_image',
            'password',
            'password2',
            'date_joined',
            'last_login',
            'is_staff',
            'is_active',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_staff', 'is_active']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """Validate registration data."""
        # Check if passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password2': _("The two password fields didn't match.")
            })
        
        # Check if email already exists (case-insensitive)
        email = attrs.get('email', '').lower()
        if Profile.objects.filter(email__iexact=email).exists():
            raise UserAlreadyExists(_('A user with this email already exists.'))
        
        # Validate password strength
        try:
            validate_password(attrs['password'])
        except Exception as e:
            raise WeakPasswordError(str(e))
        
        return attrs
    
    def create(self, validated_data):
        """Create a new user with the given validated data."""
        # Remove password2 as it's not needed for user creation
        validated_data.pop('password2', None)
        
        try:
            user = Profile._default_manager.create_user(**validated_data)
            
            # Send verification email
            if user:
                mail_subject = _('Please activate your account!')
                emails_handler.send_verification_email(
                    request=self.context.get('request'),
                    user=user,
                    template_email='account_verification_email.html',
                    mail_subject=mail_subject,
                )
            
            return user
            
        except Exception as e:
            # Log the error here if you have logging set up
            raise serializers.ValidationError({
                'non_field_errors': [_('Failed to create user. Please try again.')]
            })


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for initiating password reset.
    Sends a password reset email to the provided email address.
    """
    email = serializers.EmailField(
        required=True,
        help_text=_('The email address associated with your account')
    )
    
    def validate_email(self, value):
        """Validate that the email exists in the system."""
        try:
            return Profile.objects.get(email__iexact=value.lower())
        except Profile.DoesNotExist:
            # Don't reveal that the email doesn't exist for security reasons
            return None
    
    def validate(self, attrs):
        """Validate and process the password reset request."""
        user = attrs.get('email')
        
        # If user is None, it means validate_email didn't find the user
        # but we'll still return success for security reasons
        if user and user.is_active:
            mail_subject = _('Reset Your Password')
            emails_handler.send_verification_email(
                request=self.context.get('request'),
                user=user,
                template_email='reset_password_email.html',
                mail_subject=mail_subject,
            )
        
        # Always return the same response regardless of whether the email exists
        return {
            'detail': _(
                'If an account exists with this email, you will receive a password reset link.'
            )
        }


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for changing a user's password.
    Requires the current password and the new password (with confirmation).
    """
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text=_('Your current password')
    )
    new_password = PasswordField(
        required=True,
        help_text=_('Your new password')
    )
    new_password2 = PasswordField(
        required=True,
        help_text=_('Confirm your new password')
    )

    class Meta:
        model = Profile
        fields = (
            'old_password',
            'new_password',
            'new_password2',
        )
        extra_kwargs = {
            'old_password': {'write_only': True},
            'new_password': {'write_only': True},
            'new_password2': {'write_only': True},
        }

    def validate_old_password(self, value):
        """Verify the old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Your old password was entered incorrectly.'))
        return value

    
    
    def validate(self, attrs):
        if attrs.get('password', '') != attrs.get('password2', ''):
            raise ValueError(_("The two Passwords must be equal!"))
        
        return attrs