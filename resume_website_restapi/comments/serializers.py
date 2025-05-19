from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
# DRF
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Comment
from posts.models import Post
from users.serializers import UserSerializer
# from posts.serializers import PostListCreateSerializer


class CommentSerializer(serializers.Serializer):
    author = UserSerializer(read_only=True)
    # post = PostListCreateSerializer(read_only=True)
    image = serializers.ImageField(
        source='imageURL',
        allow_empty_file=True,
        read_only=True,
    )
    slug = serializers.SlugField(
        max_length=100, 
        allow_blank=True,
        required=False,
    )
    title = serializers.CharField(
        max_length = 100,
        allow_blank=True,
        allow_null=True,
    )
    content = serializers.CharField(
        max_length= 500,
        allow_blank=True,
        allow_null=True,
    )
    date_created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    
    
class CommentCRUDSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    # post = PostListCreateSerializer(read_only=True)
    comment_image = serializers.ImageField(
        source='imageURL',
        allow_empty_file=True,
        read_only=True,
    )
    image = serializers.ImageField(
        allow_empty_file=True,
        write_only=True,
    )
    slug = serializers.SlugField(
        max_length=100, 
        allow_blank=True,
        required=False,
        validators=[
                        UniqueValidator(queryset=Comment.objects.all()),
                ]
    )

    class Meta:
        model = Comment
        fields = (
            'title',
            'slug',
            'author',
            # 'post',
            'date_created',
            'updated',
            'content',
            'image',
            'comment_image',
        )
        
    
    def create(self, validated_data):
        request = self.context.get('request', None)
        _post_slug = request.GET.get('post_slug', '')
        
        validated_data['author'] = request.user
        try:
            validated_data['post'] = Post.objects.get(slug=_post_slug)
        except Comment.DoesNotExist:
            raise ValueError(_("Post id is not valid!"))
        
        print(validated_data)
        comment = Comment.objects.create(**validated_data)
        if not comment.slug:
            comment.slug = slugify(comment.title)
            
        comment.save()
        return comment
        
        