
from django.urls import path
from . import views

app_name = 'category'


urlpatterns = [
    path('',       
        views.CategoryListApiView.as_view(),
        name='category-list'
    ),
    path('<slug:category_slug>/posts/',       
        views.CategoryPostsListApiView.as_view(),
        name='category-posts'
    ),
    path('create/',       
        views.CategoryCreateApiView.as_view(),
        name='category-create'
    ),
    path('<slug:category_slug>/',       
        views.CategoryUpdateDestroyApiView.as_view(),
        name='category-update-delete'
    ),
    path('detail/<slug:category_slug>/',       
        views.CategoryRetrieveApiView.as_view(),
        name='category-retrieve'
    ),  
]
