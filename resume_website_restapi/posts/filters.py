# DRF filters
from django_filters import rest_framework as filters

from .models import Post


class PostsFilter(filters.FilterSet):
    content = filters.CharFilter(lookup_expr='icontains')
    
    author__username = filters.CharFilter(lookup_expr='icontains')
    author__country  = filters.CharFilter(lookup_expr='icontains')
    category__title  = filters.CharFilter(lookup_expr='icontains')
    tags__title      = filters.CharFilter(lookup_expr='icontains')
    
    
    release_date = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='created_at')
    release_data_year__gt = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='created_at__gt')
    release_data_year__lt = filters.DateTimeFilter(
        field_name='created_at', lookup_expr='created_at__lt')
    
    class Meta:
        model = Post
        fields = [
                  'content',
                  'author__username',
                  'author__country',
                  'category__title',
                  'tags__title',
                  'release_date',
                  ]
    
    