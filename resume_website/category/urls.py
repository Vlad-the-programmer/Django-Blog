from django.urls import path
from . import views

app_name = 'category'

urlpatterns = [
    path('<slug:category_slug>/',        views.CategoryPostsList.as_view(),
        name='category-posts'),
    path('update/<slug:category_slug>/', views.CategoryUpdateView.as_view(),
        name='category-update'),
    path('create/',                      views.CategoryCreateView.as_view(),
        name='category-create'),
    path('delete/<slug:category_slug>/', views.CategoryDeleteView.as_view(),
        name='category-delete'),
    
]
