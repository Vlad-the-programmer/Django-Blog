from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# DRF
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Category


class CategorySerializer(serializers.Serializer):
    """
    Serializer for category read operations.
    Used for listing and retrieving categories.
    """
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(
        max_length=100,
        allow_blank=False,
        allow_null=False,
        required=True,
        help_text=_("Category title (required, max 100 characters)")
    )
    slug = serializers.SlugField(
        max_length=100,
        read_only=True,
        help_text=_("URL-friendly version of the title (auto-generated)")
    )
    date_created = serializers.DateTimeField(read_only=True)
    date_updated = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    def validate_title(self, value):
        """Ensure title is unique (case-insensitive)."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Title cannot be empty."))
        
        if hasattr(self, 'instance'):
            # For updates, exclude current instance from the check
            if Category.objects.filter(title__iexact=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(_("A category with this title already exists."))
        elif Category.objects.filter(title__iexact=value).exists():
            raise serializers.ValidationError(_("A category with this title already exists."))
            
        return value.strip()


class CategoryCRUDSerializer(serializers.ModelSerializer):
    """
    ModelSerializer for category CRUD operations.
    Handles creation, updates, and validation of categories.
    """
    title = serializers.CharField(
        max_length=100,
        allow_blank=False,
        allow_null=False,
        required=True,
        help_text=_("Category title (required, max 100 characters)")
    )
    slug = serializers.SlugField(
        max_length=100,
        allow_blank=True,
        required=False,
        validators=[
            UniqueValidator(
                queryset=Category.objects.all(),
                message=_("This slug is already in use. Please choose another one.")
            )
        ],
        help_text=_("URL-friendly version of the title (auto-generated if not provided)")
    )
    
    class Meta:
        model = Category
        fields = (
            'id', 'title', 'slug', 'date_created', 'date_updated', 'is_active'
        )
        read_only_fields = ('id', 'date_created', 'date_updated', 'is_active')
        extra_kwargs = {
            'title': {'help_text': _('The name of the category')},
        }
    
    def validate_title(self, value):
        """Ensure title is not empty and unique (case-insensitive)."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Title cannot be empty."))
        return value.strip()
    
    def validate(self, attrs):
        """
        Object-level validation.
        If slug is not provided, generate it from the title.
        """
        # Generate slug from title if not provided
        if 'title' in attrs and not attrs.get('slug'):
            attrs['slug'] = slugify(attrs['title'])
            
        # Ensure slug is unique
        if 'slug' in attrs:
            queryset = Category.objects.filter(slug=attrs['slug'])
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({
                    'slug': _('This slug is already in use. Please choose another one.')
                })
                
        return attrs
    
    def create(self, validated_data):
        """
        Create a new category instance.
        Automatically generates a slug from the title if not provided.
        """
        # Generate slug from title if not provided
        if not validated_data.get('slug') and validated_data.get('title'):
            validated_data['slug'] = slugify(validated_data['title'])
            
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update a category instance.
        Updates the slug if the title was changed and no slug was provided.
        """
        # If title is being updated and no slug was provided, update the slug
        if 'title' in validated_data and not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data['title'])
            
        return super().update(instance, validated_data)