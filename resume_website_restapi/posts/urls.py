from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', 
         views.PostListApiView.as_view(), 
         name='posts-list'
    ),
    path('create/',       
         views.PostCreateApiView.as_view(),
         name='post-create'
    ),  
    path('<slug:post_slug>/',  
         views.PostUpdateDestroyApiView.as_view(), 
         name='post-update-delete'
    ),
     path('detail/<slug:post_slug>/',       
        views.PostRetrieveApiView.as_view(),
        name='post-retrieve'
    ),  
]
