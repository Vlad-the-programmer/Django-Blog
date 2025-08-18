from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Comment
from .serializers import CommentCRUDSerializer


@extend_schema(tags=['Comments'])
@extend_schema(parameters=[
    OpenApiParameter(
        name='slug',
        type=str,
        location=OpenApiParameter.PATH,
        description='Slug of the comment',
        required=True
    ),
])
class CommentViewSet(viewsets.ModelViewSet):
    """
    Handles listing, creating, retrieving, updating, and deleting comments.
    """
    serializer_class = CommentCRUDSerializer
    lookup_field = "slug"
    queryset = Comment.objects.none()  # Required for schema generation

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # For schema generation, return an empty queryset
            return Comment.objects.none()
            
        queryset = Comment.objects.select_related("author", "post").only(
            "id", "title", "content", "date_created", "date_updated", "slug", "image",
            "author__id", "author__username", "author__first_name", "author__last_name",
            "post__id", "post__slug", "post__title"
        ).order_by("-date_created")

        # Filter comments by post slug when listing
        if self.action == "list":
            post_slug = self.request.query_params.get("post_slug")
            if post_slug:
                queryset = queryset.filter(post__slug=post_slug)

        # Restrict update/delete to active comments only
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            queryset = Comment.active_comments.all()
            
        # Apply any filtering from the filter backend
        if hasattr(self, 'filter_backends'):
            for backend in self.filter_backends:
                queryset = backend().filter_queryset(self.request, queryset, self)

        return queryset
        
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

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()
