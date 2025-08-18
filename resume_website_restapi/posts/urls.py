from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .views import PostViewSet

app_name = 'posts'

class PostDetailView(GenericAPIView):
    """
    Handle GET, PUT, PATCH, and DELETE requests for a single post by slug.
    """
    serializer_class = PostViewSet.serializer_class
    lookup_field = 'slug'
    queryset = PostViewSet.queryset  # Will be overridden in get_queryset
    
    def get_view_name(self):
        return "Post Detail"

    def get_view_description(self, html=False):
        return "Handle operations on a single post by its slug"
        
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # For schema generation, return an empty queryset
            return self.queryset.model.objects.none()
        return PostViewSet().get_queryset()

    def get(self, request, slug, *args, **kwargs):
        view = PostViewSet.as_view({'get': 'retrieve'}, **self.get_extra_actions())
        return view(request, slug=slug)

    def put(self, request, slug, *args, **kwargs):
        view = PostViewSet.as_view({'put': 'update'}, **self.get_extra_actions())
        return view(request, slug=slug)

    def patch(self, request, slug, *args, **kwargs):
        view = PostViewSet.as_view({'patch': 'partial_update'}, **self.get_extra_actions())
        return view(request, slug=slug)

    def delete(self, request, slug, *args, **kwargs):
        view = PostViewSet.as_view({'delete': 'destroy'}, **self.get_extra_actions())
        return view(request, slug=slug)
    
    def get_extra_actions(self):
        return {
            'get_success_headers': self.get_success_headers,
            'get_success_headers': lambda x: {},
        }

# Using a custom router to define the URL pattern with slug parameter
class PostRouter(DefaultRouter):
    def get_urls(self):
        urls = super().get_urls()
        
        # Add the slug-based detail view
        slug_url = re_path(
            r'^posts/(?P<slug>[\w-]+)/$',
            PostDetailView.as_view(),
            name='post-detail'
        )
        
        # Add the comments endpoint
        comments_url = re_path(
            r'^posts/(?P<slug>[\w-]+)/comments/$',
            PostViewSet.as_view({'get': 'comments', 'post': 'comments'}),
            name='post-comments'
        )
        
        return [slug_url, comments_url] + urls

router = PostRouter()
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = router.urls
