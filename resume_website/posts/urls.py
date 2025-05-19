from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('',                         views.PostsView.as_view(), name='posts-list'),
    path('post/detail/<slug:slug>/', views.PostDetail.as_view(), name='post-detail'),
    path('post/update/<slug:slug>/', views.PostUpdate.as_view(), name='post-update'),
    path('post/create/',             views.CreatePost.as_view(), name='post-create'),
    path('post/delete/<slug:slug>/', views.PostDelete.as_view(), name='post-delete'),
    
    
]
