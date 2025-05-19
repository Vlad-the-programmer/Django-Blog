from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('comment/create/',          views.CommentCreate.as_view(), name='comment-create'),
    path('comment/update/<int:pk>/', views.CommentUpdate.as_view(), name='comment-update'),
    path('comment/delete/<int:pk>/', views.CommentDelete.as_view(), name='comment-delete'),
    
    
]
