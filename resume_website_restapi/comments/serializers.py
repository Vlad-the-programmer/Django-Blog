from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

# DRF
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# DRF Spectacular
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

# Local
from .models import Comment
from posts.models import Post
from posts.choices import STATUS as POST_STATUS
from users.serializers import UserSerializer

# Constants
MAX_TITLE_LENGTH = 100
MAX_CONTENT_LENGTH = 500
SLUG_MAX_LENGTH = 100

class CurrentUserDefault(serializers.CurrentUserDefault):
    def __call__(self, **kwargs):
        user = super().__call__(**kwargs)
        return user.id if user and user.is_authenticated else None


@extend_schema_serializer(
    exclude_fields=['author', 'post'],  # These will be handled in the view
    examples=[
        OpenApiExample(
            'Comment Example',
            value={
                'title': 'Great post!',
                'slug': 'great-post',
                'content': 'This is a sample comment content.',
                'date_created': '2023-01-01T12:00:00Z',
                'updated': '2023-01-01T12:00:00Z',
                'comment_image': 'http://example.com/media/comments/image.jpg',
                'is_active': True
            },
            response_only=True
        )
    ]
)
class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comment representation.
    Used for read operations to provide detailed comment information.
    """
    author = UserSerializer(read_only=True)
    comment_image = serializers.ImageField(
        source='imageURL',
        read_only=True,
        help_text=_('URL of the comment image')
    )
    
    class Meta:
        model = Comment
        fields = [
            'id',
            'title',
            'slug',
            'author',
            'content',
            'date_created',
            'updated',
            'comment_image',
            'is_active',
        ]
        read_only_fields = ['id', 'date_created', 'updated', 'is_active']
    
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Create Comment Example',
            value={
                'title': 'My Comment',
                'content': 'This is a sample comment.',
                'image': '<binary_data>',  # For documentation purposes
                'slug': 'my-comment'  # Optional, will be auto-generated if not provided
            },
            request_only=True
        )
    ]
)
class CommentCRUDSerializer(serializers.ModelSerializer):
    """
    Serializer for creating, updating, and deleting comments.
    Handles comment creation with automatic slug generation and post association.
    """
    author = UserSerializer(read_only=True)
    comment_image = serializers.ImageField(
        source='imageURL',
        read_only=True,
        help_text=_('URL of the comment image')
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        write_only=True,
        help_text=_('Image file to upload with the comment')
    )
    slug = serializers.SlugField(
        max_length=SLUG_MAX_LENGTH,
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[
            UniqueValidator(
                queryset=Comment.active_comments.all(),
                message=_('A comment with this slug already exists.')
            )
        ],
        help_text=_('URL-friendly version of the title. Will be auto-generated if left blank')
    )

    class Meta:
        model = Comment
        fields = [
            'id',
            'title',
            'slug',
            'author',
            'content',
            'date_created',
            'updated',
            'image',
            'comment_image',
            'is_active',
        ]
        read_only_fields = ['id', 'date_created', 'updated', 'author', 'is_active']
        extra_kwargs = {
            'title': {
                'max_length': MAX_TITLE_LENGTH,
                'min_length': 3,
                'error_messages': {
                    'max_length': _('Title cannot be longer than {max_length} characters.'),
                    'min_length': _('Title must be at least {min_length} characters long.')
                }
            },
            'content': {
                'max_length': MAX_CONTENT_LENGTH,
                'min_length': 10,
                'error_messages': {
                    'max_length': _('Comment cannot be longer than {max_length} characters.'),
                    'min_length': _('Comment must be at least {min_length} characters long.'),
                    'blank': _('Comment cannot be empty.')
                },
                'required': True,
                'allow_blank': False
            }
        }

    def validate(self, attrs):
        """
        Validate the comment data.
        """
        # Ensure content is provided and not just whitespace
        content = attrs.get('content', '').strip()
        if not content:
            raise serializers.ValidationError({
                'content': _('Comment cannot be empty or just whitespace.')
            })
            
        # Auto-generate title if not provided
        if not attrs.get('title'):
            attrs['title'] = content[:50] + '...' if len(content) > 50 else content
            
        # Auto-generate slug if not provided
        if not attrs.get('slug'):
            attrs['slug'] = self._generate_unique_slug(attrs['title'])
            
        return attrs
        
    def _generate_unique_slug(self, title):
        """
        Generate a unique slug from the title.
        """
        base_slug = slugify(title)[:SLUG_MAX_LENGTH]
        unique_slug = base_slug
        num = 1
        
        while Comment.active_comments.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{num}"
            num += 1
            
        return unique_slug
    
    def create(self, validated_data):
        """
        Create a new comment instance.
        """
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError({
                'request': _('Request object is missing from context.')
            })
            
        # Get post_slug from query params or request data
        post_slug = (
            request.query_params.get('post_slug') or 
            request.data.get('post_slug')
        )
        
        if not post_slug:
            raise serializers.ValidationError({
                'post_slug': _('Post slug is required to create a comment.')
            })
            
        try:
            # Use the default manager to find the post
            post = Post.objects.get(slug=post_slug)
            
            # If the post is not published, raise an error
            if not (post.status == POST_STATUS.PUBLISH and post.is_active):
                raise Post.DoesNotExist("Post is not published")
                
        except Post.DoesNotExist:
            raise serializers.ValidationError({
                'post_slug': _('No post found with the given slug.')
            })
        
        # Set the post and author
        validated_data['post'] = post
        validated_data['author'] = request.user
        
        # Handle image upload
        if 'image' in validated_data and validated_data['image'] is None:
            del validated_data['image']
            
        # Create the comment
        comment = Comment._default_manager.create(**validated_data)
        return comment
        
    def update(self, instance, validated_data):
        """
        Update an existing comment instance.
        """
        # Only allow updating specific fields
        editable_fields = ['title', 'content', 'image', 'is_active']
        for field in editable_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
                
        # Update the slug if title was changed
        if 'title' in validated_data:
            instance.slug = self._generate_unique_slug(validated_data['title'])
            
        instance.save()
        return instance
        
        