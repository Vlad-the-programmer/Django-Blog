from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema

from .models import Category
from .serializers import CategoryCRUDSerializer
from posts.serializers import PostListSerializer


@extend_schema(tags=['Categories'])
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Handles listing, retrieving, creating, updating, and deleting categories.
    Includes a custom action to list posts inside a category.
    """
    serializer_class = CategoryCRUDSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "category_slug"

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return Category.objects.filter(is_active=True).only(
                "id", "title", "slug", "date_created", "date_updated"
            )
        return Category.objects.all()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Category deleted successfully."},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        description="List all posts in a category",
        responses={200: PostListSerializer(many=True)}
    )
    @action(detail=True, methods=["get"], url_path="posts", url_name="posts")
    def list_posts(self, request, category_slug=None):
        """
        Custom action: /categories/{slug}/posts/
        Returns all active posts inside this category.
        """
        try:
            category = self.get_object()
        except Category.DoesNotExist:
            raise NotFound("Category not found")

        posts = category.posts.filter(is_active=True).select_related(
            "author", "category"
        ).prefetch_related("tags").only(
            "id", "title", "slug", "excerpt", "image", "date_created",
            "author__id", "author__username", "category__id", "category__title"
        )
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
