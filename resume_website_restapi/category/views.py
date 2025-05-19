from django.utils.decorators import method_decorator
# REST FRAMEWORK
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
# Generic views and mixins
from rest_framework import generics


from .models import Category
from .serializers import CategoryCRUDSerializer


class CategoryListApiView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCRUDSerializer
    permission_classes = (AllowAny,)
    

class CategoryRetrieveApiView(generics.RetrieveAPIView):
    serializer_class = CategoryCRUDSerializer
    
    
    def get_object(self):
        _category_slug = self.kwargs.get('category_slug', '')
        try:
            category = Category.objects.get(slug=_category_slug)
        except Category.DoesNotExist:
            category = None
            
        return category
    
    
class CategoryCreateApiView(generics.CreateAPIView):
    serializer_class = CategoryCRUDSerializer
    permission_classes = (IsAdminUser,)
    
    
    def post(self, request, *args, **kwargs):
        print(request.user)
        return super().post(request, *args, **kwargs)
    
    
class CategoryUpdateDestroyApiView(generics.UpdateAPIView,
                                   generics.DestroyAPIView,
                                ):
    serializer_class = CategoryCRUDSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    
    
    def get_object(self):
        _category_slug = self.kwargs.get('category_slug', '')
        try:
            category = Category.objects.get(slug=_category_slug)
        except Category.DoesNotExist:
            category = None
            
        return category
    
    
    def destroy(self, request, *args, **kwargs):
        print(self.get_object())
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Deleted successfully!"},
            status=status.HTTP_200_OK,
        )
         
    
class CategoryPostsListApiView(generics.ListAPIView):
    serializer_class = CategoryCRUDSerializer
    
    
    def get_queryset(self):
        _category_slug = self.kwargs.get('category_slug', '')
        try:
            category = Category.objects.get(slug=_category_slug)
            posts = category.posts.all()
        except Category.DoesNotExist:
            category = None
            posts = None
            
        return posts
    