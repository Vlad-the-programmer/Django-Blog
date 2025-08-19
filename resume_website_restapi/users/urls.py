from django.urls import path
from .views import UserViewSet

app_name = 'users'

urlpatterns = [
    # List and Create
    path('', UserViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='user-list'),
    
    # Retrieve and Update
    path('<int:pk>/', UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
    }), name='user-detail'),
    
    # Custom delete profile endpoint
    path('<int:pk>/delete-profile/', 
         UserViewSet.as_view({'delete': 'delete_profile'}), 
         name='user-delete-profile'),
]
