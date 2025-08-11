from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.serializers import UserSerializer
from comments.serializers import CommentSerializer
from category.serializers import CategorySerializer
from category.models import Category
from .models import Post, Tags


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'title', 'date_created']
        read_only_fields = ['id', 'date_created']

class PostListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    slug = serializers.SlugField(
        max_length=100,
        allow_blank=True,
        required=False,
        validators=[UniqueValidator(queryset=Post.published.all())]
    )

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'image',
            'slug',
            'date_created',
            'date_updated',
            'status',
            'author',
            'tags',
            'category',
            'comments',
        )
        read_only_fields = ['id', 'date_created', 'date_updated']


class PostCRUDSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    # For writing tags - accept list of tag IDs or titles
    add_tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    category = CategorySerializer(read_only=True)

    # For writing category - accept category ID
    add_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    slug = serializers.SlugField(
        max_length=100,
        allow_blank=True,
        required=False,
        validators=[UniqueValidator(queryset=Post.published.all())]
    )

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'image',
            'slug',
            'date_created',
            'updated',
            'status',
            'author',
            'tags',
            'add_tags',
            'category',
            'add_category',
            'comments',
        )
        read_only_fields = ['id', 'date_created', 'updated']

    def create(self, validated_data):
        request = self.context.get('request')
        tags_data = validated_data.pop('add_tags', [])
        category = validated_data.pop('add_category', None)

        # Handle slug generation
        title = validated_data.get('title', '')
        slug = validated_data.get('slug', '')

        if not slug:
            slug = slugify(title)

        validated_data['slug'] = slug.lower()

        # Set author from request user
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user

        try:
            post = Post._default_manager.create(**validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                _("Error creating post: {}").format(str(e))
            )

        # Handle tags
        if tags_data:
            self._process_tags(post, tags_data)

        # Handle category
        if category:
            post.category = category
            post.save()

        return post

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('add_tags', None)
        category = validated_data.pop('add_category', None)

        # Handle slug if title changes
        if 'title' in validated_data and not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data['title']).lower()

        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update tags if provided
        if tags_data is not None:
            instance.tags.clear()
            self._process_tags(instance, tags_data)

        # Update category if provided
        if category is not None:
            instance.category = category

        instance.save()
        return instance

    def _process_tags(self, post, tags_data):
        """Helper method to process tags from input data"""
        existing_tags = Tags.objects.filter(title__in=tags_data)
        existing_tag_titles = set(tag.title for tag in existing_tags)

        # Create new tags for any that don't exist
        new_tags = []
        for tag_title in tags_data:
            if tag_title not in existing_tag_titles:
                new_tag = Tags.objects.create(title=tag_title)
                new_tags.append(new_tag)

        # Add all tags to the post
        post.tags.add(*existing_tags, *new_tags)

    def get_comments(self, obj):
        comments = obj.comments.all().order_by('-date_created')
        return CommentSerializer(comments, many=True).data

    def validate_title(self, value):
        """
        Check that the title is unique.
        Exclude current instance when updating.
        """
        instance = getattr(self, 'instance', None)
        if instance and Post.objects.exclude(pk=instance.pk).filter(title=value).exists():
            raise serializers.ValidationError(_("A post with this title already exists."))
        elif not instance and Post.objects.filter(title=value).exists():
            raise serializers.ValidationError(_("A post with this title already exists."))
        return value