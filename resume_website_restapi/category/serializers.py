from django.utils.text import slugify
# DRF
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Category


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(
        max_length=100,
        allow_blank=True,
        allow_null=True,
    )
    slug = serializers.SlugField(
        max_length=100,
        allow_blank=True,
        required=False,
        validators=[
                        UniqueValidator(queryset=Category.objects.all()),
                ]
    )
    
    
class CategoryCRUDSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=100,
        allow_blank=True,
        required=False,
        validators=[
                        UniqueValidator(queryset=Category.objects.all()),
                ]
    )
    class Meta:
        model = Category
        fields = (
            'title',
            'slug'
        )
        
    def create(self, validated_data):
        title = validated_data["title"]
        
        category = Category.objects.create(**validated_data)
        if not category.slug:
            category.slug = slugify(title)

        category.save()
        
        return category
            
            