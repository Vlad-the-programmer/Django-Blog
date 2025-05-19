# DRF
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

from .serializers import CommentCRUDSerializer
from .models import Comment


class CommentListCreateApiView(generics.ListCreateAPIView):
    serializer_class = CommentCRUDSerializer
    
    
    def get_queryset(self):
        _post_slug = self.request.query_params.get('post_slug', '')
        print(_post_slug)
        try:
            queryset = Comment.objects.filter(post__slug=_post_slug)
        except Comment.DoesNotExist:
            queryset = None
        
        return queryset


class CommentRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentCRUDSerializer
    lookup_field = 'slug'
    
    
    def get_object(self):
        _slug = self.kwargs.get('slug', '')
        user = self.request.user
        
        try:
            comment = user.comments.get(slug=_slug)
        except Comment.DoesNotExist:
            comment = None
            
        return comment
    
    
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {'detail': 'Deleted!'},
            status=status.HTTP_200_OK,
        )
        
