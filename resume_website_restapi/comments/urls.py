from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from . import views

app_name = "comments"

class CommentDetailView(GenericAPIView):
    """
    Handle GET, PUT, PATCH, and DELETE requests for a single comment by slug.
    """
    serializer_class = views.CommentCRUDSerializer
    lookup_field = 'slug'
    queryset = views.Comment.objects.none()  # Will be overridden in get_queryset
    
    def get_view_name(self):
        return "Comment Detail"

    def get_view_description(self, html=False):
        return "Handle operations on a single comment by its slug"
        
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # For schema generation, return an empty queryset
            return views.Comment.objects.none()
        return views.Comment.objects.all()

    def get(self, request, slug, *args, **kwargs):
        view = views.CommentViewSet.as_view({'get': 'retrieve'}, **self.get_extra_actions())
        return view(request, slug=slug)

    def put(self, request, slug, *args, **kwargs):
        view = views.CommentViewSet.as_view({'put': 'update'}, **self.get_extra_actions())
        return view(request, slug=slug)

    def patch(self, request, slug, *args, **kwargs):
        view = views.CommentViewSet.as_view({'patch': 'partial_update'}, **self.get_extra_actions())
        return view(request, slug=slug)

    def delete(self, request, slug, *args, **kwargs):
        view = views.CommentViewSet.as_view({'delete': 'destroy'}, **self.get_extra_actions())
        return view(request, slug=slug)
    
    def get_extra_actions(self):
        return {
            'get_success_headers': lambda x: {},
        }

# Using a custom router to define the URL pattern with slug parameter
class CommentRouter(DefaultRouter):
    def get_urls(self):
        urls = super().get_urls()
        
        # Add the slug-based detail view
        slug_url = re_path(
            r'^comments/(?P<slug>[\w-]+)/$',
            CommentDetailView.as_view(),
            name='comment-detail'
        )
        
        return [slug_url] + urls

router = CommentRouter()
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = router.urls