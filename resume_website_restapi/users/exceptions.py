from django.utils.translation import gettext_lazy as _
# REST FRAMEWORK
from rest_framework.exceptions import APIException


class NotOwner(APIException):
    status_code = 403
    default_detail = _('You cannot access a profile if you are not it\'s owner!!!')
    default_code = 'access_denied'
    
    
class UserOrTokenNotValid(APIException):
    status_code = 406
    default_detail = _("User is None or token is not valid!")
    default_code = 'activation_not_successful'
    
    
class UserAlreadyExists(APIException):
    status_code = 302
    default_detail = _("User with this email already exists!")
    default_code = 'user_exists' 