from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_countries.widgets import CountrySelectWidget
from allauth.account import forms as login_form
# # Signal 
# from django.db.models.signals import post_save
# from .signals import update_user_profile


Profile = get_user_model()


class UserUpdateForm(UserChangeForm):
    featured_img = forms.ImageField(required=False)
    class Meta:
        model = Profile
        fields = (
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'country',
                  'featured_img',
                  'gender',
                  )
        exclude = ['password']

    
    # def save(self, *args, **kwargs):
    #     profile = super().save(commit=False)
    #     post_save.disconnect(update_user_profile, sender=Profile)
    #     profile.save()
    #     post_save.connect(update_user_profile, sender=Profile)
        
    
class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Profile
        fields = (
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'country',
                  'featured_img',
                  'gender',
                )
        widgets = {'country': CountrySelectWidget()}
        
        
class UserLoginForm(login_form.LoginForm):
    class Meta:
        def __init__(self):
            super(login_form.LoginForm, self).__init__()
            for field in self.fields:
                field.update({'class': 'form-control'})
        

class UserPasswordResetForm(forms.ModelForm):
    confirm_password = forms.PasswordInput(attrs={'placeholder': 'Confirm password'})
    class Meta:
        model = Profile
        fields = ('password',)
        widgets = {'password': forms.PasswordInput(attrs={'placeholder': 'New password'})}
        