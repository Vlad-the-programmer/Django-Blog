from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import generics
from django_filters import rest_framework as filters

from .models import Post
from .serializers import PostCRUDSerializer
from . import filters as custom_filters


@extend_schema(
    tags=['Posts'],
    description="List all active blog posts with filtering capabilities"
)
class PostListApiView(generics.ListAPIView):
    """
    List all active blog posts with filtering capabilities.
    Optimized with select_related and prefetch_related for better performance.
    """
    serializer_class = PostCRUDSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = custom_filters.PostsFilter

    def get_queryset(self):
        """
        Optimize the queryset with select_related and prefetch_related.
        Only fetch the fields that are needed for the list view.
        """
        return Post.objects.filter(active=True).select_related(
            'author',      # ForeignKey to User model
            'category'     # ForeignKey to Category model
        ).prefetch_related(
            'tags',        # ManyToMany to Tags model
            'comments'     # Reverse relation to Comment model
        ).only(
            # Post model fields
            'id', 'title', 'slug', 'content', 'image', 'active',
            'date_created', 'date_updated', 'status',
            
            # Author fields
            'author__id', 'author__username', 'author__first_name', 'author__last_name',
            
            # Category fields
            'category__id', 'category__name', 'category__slug'
        ).order_by('-date_created')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='category',
                description='Filter by category ID',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='author',
                description='Filter by author ID',
                required=False,
                type=int
            ),
        ],
        examples=[
            OpenApiExample(
                'Example response',
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "title": "Sample Post",
                            "slug": "sample-post",
                            # ... other fields
                        }
                    ]
                }
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    tags=['Posts'],
    description="Create a new blog post (Admin only)"
)
class PostCreateApiView(generics.CreateAPIView):
    serializer_class = PostCRUDSerializer
    permission_classes = (IsAdminUser,)

    @extend_schema(
        request=PostCRUDSerializer,
        responses={
            201: OpenApiResponse(
                description="Post created successfully",
                response=PostCRUDSerializer
            ),
            400: OpenApiResponse(description="Invalid input data")
        }
    )
    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(
            data={'detail': 'Created!'},
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=['Posts'],
    description="Update or delete a blog post (Admin only)"
)
class PostUpdateDestroyApiView(generics.UpdateAPIView,
                             generics.DestroyAPIView):
    """
    Update or delete a blog post (Admin only).
    Optimized with select_related and prefetch_related for better performance.
    """
    serializer_class = PostCRUDSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'post_slug'
    
    def get_queryset(self):
        """
        Optimize the queryset with select_related and prefetch_related.
        Only fetch the fields that are needed for the update/delete operations.
        """
        return Post.published.select_related(
            'author',       # ForeignKey to User model
            'category'      # ForeignKey to Category model
        ).prefetch_related(
            'tags'          # ManyToMany to Tags model (needed for updates)
        ).only(
            # Post model fields needed for update/delete
            'id', 'title', 'slug', 'content', 'image', 'active',
            'date_created', 'date_updated', 'status',
            
            # ForeignKey fields
            'author__id', 'category__id',
            
            # Fields needed for tag updates
            'tags__id', 'tags__title'
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='post_slug',
                description='Post slug identifier',
                required=True,
                type=str
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Post updated successfully",
                response=PostCRUDSerializer
            ),
            404: OpenApiResponse(description="Post not found")
        }
    )
    def get_object(self):
        """Retrieve a single post with optimized queries."""
        try:
            return self.get_queryset().get(slug=self.kwargs.get('post_slug'))
        except Post.DoesNotExist:
            return None

    @extend_schema(
        request=PostCRUDSerializer,
        responses={
            200: OpenApiResponse(
                description="Post updated successfully",
                response=PostCRUDSerializer
            ),
            400: OpenApiResponse(description="Invalid input data")
        }
    )
    def perform_update(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(
            data={'detail': 'Updated!'},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Post deleted successfully"),
            404: OpenApiResponse(description="Post not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {'detail': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Deleted!'},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Posts'],
    description="Retrieve a single blog post by slug"
)
class PostRetrieveApiView(generics.RetrieveAPIView):
    """
    Retrieve a single blog post with all related data.
    Optimized with select_related and prefetch_related for better performance.
    """
    serializer_class = PostCRUDSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'post_slug'
    
    def get_queryset(self):
        """
        Optimize the queryset with select_related and prefetch_related.
        Fetch all necessary related data in a single query.
        """
        return Post.published.select_related(
            'author',       # ForeignKey to User model
            'category'      # ForeignKey to Category model
        ).prefetch_related(
            'tags',         # ManyToMany to Tags model
            'comments',     # Reverse relation to Comment model
            'comments__author'  # For showing comment authors
        ).only(
            # Post model fields
            'id', 'title', 'slug', 'content', 'image', 'active',
            'date_created', 'date_updated', 'status',
            
            # Author fields
            'author__id', 'author__username', 'author__first_name', 'author__last_name',
            
            # Category fields
            'category__id', 'category__name', 'category__slug',
            
            # Comment fields (for prefetch_related)
            'comments__id', 'comments__content', 'comments__date_created',
            'comments__author__id', 'comments__author__username',
            
            # Tag fields (for prefetch_related)
            'tags__id', 'tags__title'
        )
    
    def get_object(self):
        """Retrieve a single post with optimized queries."""
        try:
            return self.get_queryset().get(slug=self.kwargs.get('post_slug'))
        except Post.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {'detail': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)