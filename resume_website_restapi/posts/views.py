from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from comments.models import Comment
from comments.serializers import CommentCRUDSerializer
from .models import Post
from .serializers import PostCRUDSerializer
from . import filters as custom_filters


@extend_schema(tags=['Posts'])
@extend_schema(parameters=[
    OpenApiParameter(
        name='slug',
        type=str,
        location=OpenApiParameter.PATH,
        description='Slug of the post',
        required=True
    ),
])
class PostViewSet(viewsets.ModelViewSet):
    """
    Handles listing, retrieving, creating, updating, and deleting posts.
    Permissions and querysets are customized per action.
    """
    serializer_class = PostCRUDSerializer
    filterset_class = custom_filters.PostsFilter
    lookup_field = 'slug'
    queryset = Post.objects.none()  # Required for schema generation

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # For schema generation, return an empty queryset
            return Post.objects.none()
            
        queryset = Post.published.all()
        
        if self.action == "list":
            queryset = queryset.select_related(
                "author", "category"
            ).prefetch_related("tags", "comments").only(
                "id", "title", "slug", "content", "image", "active",
                "date_created", "date_updated", "status",
                "author__id", "author__username", "author__first_name", "author__last_name",
                "category__id", "category__name", "category__slug",
            ).order_by("-date_created")

        elif self.action in ["update", "partial_update", "destroy"]:
            queryset = queryset.select_related("author", "category").prefetch_related(
                "tags"
            ).only(
                "id", "title", "slug", "content", "image", "active",
                "date_created", "date_updated", "status",
                "author__id", "category__id",
                "tags__id", "tags__title",
            )

        elif self.action in ["retrieve", "comments"]:
            queryset = queryset.select_related("author", "category").prefetch_related(
                "tags", "comments", "comments__author"
            ).only(
                "id", "title", "slug", "content", "image", "active",
                "date_created", "date_updated", "status",
                "author__id", "author__username", "author__first_name", "author__last_name",
                "category__id", "category__name", "category__slug",
                "comments__id", "comments__content", "comments__date_created",
                "comments__author__id", "comments__author__username",
                "tags__id", "tags__title",
            )
        else:
            queryset = Post.published.none()
            
        # Apply any filtering from the filter backend
        if hasattr(self, 'filter_backends'):
            for backend in self.filter_backends:
                queryset = backend().filter_queryset(self.request, queryset, self)
                
        return queryset

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
        
    def get_object(self):
        """
        Override to handle slug-based lookups.
        """
        if 'slug' in self.kwargs:
            queryset = self.filter_queryset(self.get_queryset())
            obj = queryset.get(slug=self.kwargs['slug'])
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()
        
    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None, slug=None):
        """
        Handle listing and creating comments for a specific post.
        """
        post = self.get_object()
        
        if request.method == 'GET':
            # List all comments for the post
            comments = Comment.objects.filter(post=post, is_active=True).select_related('author')
            serializer = CommentCRUDSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data)
            
        elif request.method == 'POST':
            # Create a new comment for the post
            serializer = CommentCRUDSerializer(
                data=request.data,
                context={'request': request, 'post': post}
            )
            if serializer.is_valid():
                serializer.save(author=request.user, post=post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
