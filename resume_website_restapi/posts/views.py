from django.utils.decorators import method_decorator
# REST FRAMEWORK
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
                                            IsAdminUser, 
                                            AllowAny,
                                        )
# Generic Api Views
from rest_framework import mixins
from rest_framework import generics
# Django-Filters
from django_filters import rest_framework as filters

from .models import Post
from .serializers import PostCRUDSerializer
from . import filters as custom_filters


class PostListApiView(generics.ListAPIView):
    queryset = Post.objects.filter(active=True)
    serializer_class = PostCRUDSerializer
    permission_classes = (AllowAny, )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = custom_filters.PostsFilter
    
    
class PostCreateApiView(generics.CreateAPIView):
    serializer_class = PostCRUDSerializer
    permission_classes = (IsAdminUser, )
    
    
    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        
        return Response(
            data={'detail': 'Created!'}, 
            status=status.HTTP_201_CREATED
        )
      
      
class PostUpdateDestroyApiView(generics.UpdateAPIView,
                               generics.DestroyAPIView,
                            ):
    serializer_class = PostCRUDSerializer
    permission_classes = (IsAdminUser, )
    lookup_field = 'slug'
    lookup_url_kwarg = 'post_slug'
    
    
    def get_object(self):
        _post_slug = self.kwargs.get('post_slug', '')
        try:
            post = Post.objects.filter(active=True).get(slug=_post_slug)
        except Post.DoesNotExist:
            post = None
            
        return post
            
    
    def perform_update(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        
        return Response(
            data={'Ok': 201}, 
            status=status.HTTP_200_OK,
        )
        
                
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {'status': 'Deleted!'}, 
            status=status.HTTP_200_OK,
        )
   
   
class PostRetrieveApiView(generics.RetrieveAPIView):
    serializer_class = PostCRUDSerializer
    
    
    def get_object(self):
        _post_slug = self.kwargs.get('post_slug', '')
        try:
            post = Post.objects.filter(active=True).get(slug=_post_slug)
        except Post.DoesNotExist:
            post = None
            
        return post
    
