from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
# REST_FRAMEWORK
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django_countries.serializer_fields import CountryField


from base_utils import emails_handler
from .models import Gender
from .exceptions import NotOwner, UserAlreadyExists


Profile = get_user_model()


class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        max_length=100,
        required=False,
    )
    last_name = serializers.CharField(
        max_length=100,
        required=False,
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                            queryset=Profile.objects.filter(is_active=True),
                        ),
        ]
    )
    gender = serializers.ChoiceField(
        choices=Gender,
        allow_blank=True,
        allow_null=True,
    )
    country = CountryField(required=False)
    featured_image = serializers.ImageField(
        allow_empty_file=True,
        required=False
    )
    username = serializers.CharField(
        max_length=100,
        required=False,
    )
    is_staff = serializers.BooleanField(
        default=False,
        allow_null=True,
        read_only=True,
    )
    is_active = serializers.BooleanField(
        default=False,
        allow_null=True,
        read_only=True,
    )
    
    
    def get_cleaned_data(self):
        return {
            'username':       self.validated_data.get('username', ''),
            'email':          self.validated_data.get('email', ''),
            'first_name':     self.validated_data.get('first_name', ''),
            'last_name':      self.validated_data.get('last_name', ''),
            'country':        self.validated_data.get('country', ''),
            'gender':         self.validated_data.get('gender', ''),
            'featured_img': self.validated_data.get('featured_img', ''),
        }
    
    
    def update(self, instance, validated_data):
        request = self.context.get('request', None)
        if Profile.objects.get(id=instance.id) != request.user:
            raise NotOwner
        
        data = self.get_cleaned_data()
        instance.username = data['username'].lower() or instance.username
        instance.email = data['email'] or instance.email
        instance.first_name = data['first_name'] or instance.first_name
        instance.last_name = data['last_name'] or instance.last_name
        instance.country = data['country'] or instance.country
        instance.gender = data['gender'] or instance.gender
        instance.featured_img = data['featured_img'] or instance.featured_img

        instance.save()
        return instance
    
    
class UserRegisterSerializer(serializers.ModelSerializer):
    country = CountryField(required=False)
    password2 = serializers.CharField(
        max_length=100,
        allow_blank=True,
        allow_null=True,
        required=False,
        write_only=True,
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                                queryset=Profile.objects.filter(is_active=True),
                            ),
      ]
    )
    last_login = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Profile
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            'gender',
            'country',
            'featured_img',
            'password',
            'password2',
            'date_joined',
            'last_login',
            'is_staff',
            'is_active',
        )
        

    def create(self, validated_data):
        print('Create val_data', validated_data)
        validated_data.pop('password2')
        print('Create val_data2', validated_data)
        
        user = Profile.objects.create_user(**validated_data)
        
        if user:
            mail_subject = 'Please activate your account!'
            emails_handler.send_verification_email(
                self.context.get('request', None),
                user,
                template_email='account_verification_email.html',
                mail_subject = mail_subject,
            ) 
        
        return user
    
    
    def validate(self, attrs):
        try:
            profile = Profile.objects.get(email=attrs.get('email', ''))
        except Profile.DoesNotExist:
            pass
        else:
            raise UserAlreadyExists
        

        if attrs.get('password', '') != attrs.get('password2', ''):
            raise ValueError(_("The two Passwords must be equal!"))
        
        return attrs
    

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate(self, attrs):
        email = attrs.get('email', '')
        
        user = Profile.objects.get(email=email)
        
        if not user:
            raise Profile.DoesNotExist
        
        if user:
            mail_subject = 'Please confirm the password reset action by \
                            clicking on the link!'
            emails_handler.send_verification_email(
                self.context.get('request', None),
                user,
                template_email='reset_password_email.html',
                mail_subject = mail_subject,
            ) 
        
        return attrs
    
    
    
class ChangePasswordSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        max_length=100,
        allow_blank=True,
        allow_null=True,
        required=False,
        write_only=True,
    )
    class Meta:
        model = Profile
        fields = (
            'password',
            'password2',
        )
        
    
    def update(self, instance, validated_data):
        request = self.context.get('request', None)
        print('Val data', validated_data)
        password = validated_data.get('password', '')
        
        # if Profile.objects.get(id=instance.id) != request.user:
        #     raise NotOwner
        
        instance.set_password(password)
        instance.save()
        
        return instance
    
    
    def validate(self, attrs):
        if attrs.get('password', '') != attrs.get('password2', ''):
            raise ValueError(_("The two Passwords must be equal!"))
        
        return attrs