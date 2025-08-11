from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

# REST FRAMEWORK
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, filters
from rest_framework.exceptions import NotFound, PermissionDenied

# DRF Spectacular
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

# Local imports
from .models import Category
from .serializers import CategoryCRUDSerializer
from posts.serializers import PostListSerializer


@extend_schema(
    tags=['Categories'],
    description="List all categories with optional search and pagination"
)
class CategoryListApiView(generics.ListAPIView):
    """
    API endpoint that allows categories to be viewed.
    """
    serializer_class = CategoryCRUDSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'slug']
    ordering_fields = ['title', 'date_created', 'date_updated']
    ordering = ['title']
    
    def get_queryset(self):
        """
        Return a queryset of all active categories.
        Can be filtered by search query parameter.
        """
        queryset = Category.objects.filter(is_active=True)
        return queryset


@extend_schema(
    tags=['Categories'],
    description="Retrieve a single category by slug"
)
class CategoryRetrieveApiView(generics.RetrieveAPIView):
    """
    API endpoint that retrieves a single category by its slug.
    """
    serializer_class = CategoryCRUDSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    
    def get_queryset(self):
        """Optimized queryset with select_related and only necessary fields."""
        return Category.objects.filter(is_active=True).only(
            'id', 'title', 'slug', 'date_created', 'date_updated'
        )
    
    def get_object(self):
        """Retrieve and return the category or raise 404 if not found."""
        slug = self.kwargs.get('category_slug')
        try:
            return self.get_queryset().get(slug=slug)
        except Category.DoesNotExist:
            raise NotFound(_('Category not found'))


@extend_schema(
    tags=['Categories'],
    description="Create a new category (Admin only)"
)
class CategoryCreateApiView(generics.CreateAPIView):
    """
    API endpoint that allows creation of a new category (Admin only).
    """
    serializer_class = CategoryCRUDSerializer
    permission_classes = (IsAdminUser,)
    
    def perform_create(self, serializer):
        """Save the category with the current user as the creator."""
        serializer.save()


@extend_schema(
    tags=['Categories'],
    description="Update or delete a category (Admin only)"
)
class CategoryUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows updating or deleting a category (Admin only).
    """
    serializer_class = CategoryCRUDSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    
    def get_queryset(self):
        """Return the queryset for the view."""
        return Category.objects.all()
    
    def get_object(self):
        """Retrieve and return the category or raise 404 if not found."""
        slug = self.kwargs.get('category_slug')
        try:
            return self.get_queryset().get(slug=slug)
        except Category.DoesNotExist:
            raise NotFound(_('Category not found'))
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete the category and return a success response.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": _("Category deleted successfully.")},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Categories'],
    description="List all posts in a category"
)
class CategoryPostsListApiView(generics.ListAPIView):
    """
    API endpoint that lists all posts in a specific category.
    """
    serializer_class = PostListSerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """
        Return a queryset of all active posts in the specified category.
        """
        category_slug = self.kwargs.get('category_slug')
        try:
            category = Category.objects.get(slug=category_slug, is_active=True)
            return category.posts.filter(is_active=True).select_related(
                'author', 'category'
            ).prefetch_related('tags').only(
                'id', 'title', 'slug', 'excerpt', 'image', 'date_created',
                'author__id', 'author__username', 'category__id', 'category__title'
            )
        except Category.DoesNotExist:
            raise NotFound(_('Category not found'))