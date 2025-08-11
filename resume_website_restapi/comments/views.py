# DRF
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

# DRF Spectacular
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)

# Local
from .serializers import CommentCRUDSerializer
from .models import Comment


@extend_schema(
    tags=['Comments'],
    description="List all comments for a specific post or create a new comment"
)
class CommentListCreateApiView(generics.ListCreateAPIView):
    """
    List all comments for a specific post or create a new comment.
    Optimized with select_related and prefetch_related for better performance.
    """
    serializer_class = CommentCRUDSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def get_queryset(self):
        """
        Optimize the queryset with select_related.
        Only fetch the fields that are needed for the list view.
        """
        queryset = Comment.objects.select_related(
            'author',  # ForeignKey to User model
            'post'     # ForeignKey to Post model
        ).only(
            'id', 'title', 'content', 'date_created', 'date_updated', 'slug', 'image',
            'author__id', 'author__username', 'author__first_name', 'author__last_name',
            'post__id', 'post__slug', 'post__title'
        ).order_by('-date_created')
        
        # Filter by post_slug if provided
        post_slug = self.request.query_params.get('post_slug')
        if post_slug:
            queryset = queryset.filter(post__slug=post_slug)
            
        return queryset
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='post_slug',
                description='Filter comments by post slug',
                required=True,
                type=str,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=CommentCRUDSerializer(many=True),
                description='List of comments for the specified post'
            ),
            400: OpenApiResponse(description='Invalid post slug provided')
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=CommentCRUDSerializer,
        responses={
            201: OpenApiResponse(
                response=CommentCRUDSerializer,
                description='Comment created successfully'
            ),
            400: OpenApiResponse(description='Invalid comment data')
        }
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema(
    tags=['Comments'],
    description="Retrieve, update, or delete a comment (Owner or Admin only)"
)
class CommentRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a comment.
    Optimized with select_related and prefetch_related for better performance.
    """
    serializer_class = CommentCRUDSerializer
    lookup_field = 'slug'
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """
        Optimize the queryset with select_related.
        Only fetch the fields that are needed for the detail view.
        """
        return Comment.active_comments.select_related(
            'author',  # ForeignKey to User model
            'post'     # ForeignKey to Post model
        ).only(
            'id', 'title', 'content', 'date_created', 'date_updated', 'slug', 'image',
            'is_active', 'author__id', 'author__username', 'author__first_name', 'author__last_name',
            'post__id', 'post__slug', 'post__title'
        )
    
    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=CommentCRUDSerializer,
                description='Comment details'
            ),
            403: OpenApiResponse(description='Not authorized to view this comment'),
            404: OpenApiResponse(description='Comment not found')
        }
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        request=CommentCRUDSerializer,
        responses={
            200: OpenApiResponse(
                response=CommentCRUDSerializer,
                description='Comment updated successfully'
            ),
            400: OpenApiResponse(description='Invalid comment data'),
            403: OpenApiResponse(description='Not authorized to update this comment'),
            404: OpenApiResponse(description='Comment not found')
        }
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        request=CommentCRUDSerializer,
        responses={
            200: OpenApiResponse(
                response=CommentCRUDSerializer,
                description='Comment partially updated successfully'
            ),
            400: OpenApiResponse(description='Invalid comment data'),
            403: OpenApiResponse(description='Not authorized to update this comment'),
            404: OpenApiResponse(description='Comment not found')
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description='Comment deleted successfully',
                examples={
                    'application/json': {
                        'detail': 'Comment deleted successfully!'
                    }
                }
            ),
            403: OpenApiResponse(description='Not authorized to delete this comment'),
            404: OpenApiResponse(description='Comment not found')
        }
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def get_object(self):
        slug = self.kwargs.get('slug')
        try:
            comment = Comment.active_comments.get(slug=slug)
            # Only allow the comment owner or admin to modify/delete
            if comment.author != self.request.user and not self.request.user.is_staff:
                raise Comment.DoesNotExist
            return comment
        except Comment.DoesNotExist:
            return None
    
    def perform_destroy(self, instance):
        instance.delete()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Comment deleted successfully!'},
            status=status.HTTP_200_OK
        )
        
