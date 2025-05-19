from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
# REST FRAMEWORK
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.serializers import UserSerializer
from comments.serializers import CommentSerializer
from category.serializers import CategorySerializer
from category.models import Category

from .models import Post, Tags


class TagsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
        
        
class PostCRUDSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(read_only=True, many=True)
    comments = serializers.SerializerMethodField()
    add_tags = serializers.MultipleChoiceField(
                write_only=True,
                choices=list(Tags.objects.all()),
                allow_blank=True,
                allow_null=True
    )
    category = CategorySerializer(read_only=True)
    add_category = serializers.ChoiceField(
                write_only=True,
                choices=list(Category.objects.all()),
                allow_blank=True,
                allow_null=True
    )
    slug = serializers.SlugField(
        max_length=100, 
        allow_blank=True,
        required=False,
        validators=[
                        UniqueValidator(queryset=Post.objects.all()),
                ]
    )
    
    class Meta:
        model = Post
        fields = (
            'title', 
            'content',
            'image',
            'slug',
            'created_at',
            'updated',
            'status',
            'author',
            'tags',
            'add_tags',
            'category',
            'add_category',
            'comments',
        )
        
    def create(self, validated_data):
        print(validated_data)
        popped_tags = validated_data.pop('add_tags')
        popped_category = validated_data.pop('add_category')
        
        title = validated_data.get('title', '')
        slug = validated_data.get('slug', '')
        
        if not slug:
            slug = slugify(title)
            
        slug.lower()
            
        validated_data['title'] = title
        validated_data['slug'] = slug

        try:
            post = Post.objects.create(**validated_data)
        except:
            raise ValueError(_("Title should be unique! Or enter your own slug that is not equal to the title ot lowercased one!"))
        
        for cleaned_tag in popped_tags:
            tag = Tags.objects.get(title=cleaned_tag.title)
            post.tags.add(tag)
        
        post.category = popped_category
        
        post.save()
        
        return post
        

    def update(self, instance, validated_data):
        print('Val ', validated_data)
        
        instance.title = validated_data.get('title') or instance.title
        instance.content = validated_data.get('content') or instance.content
        instance.image = validated_data.get('image') or instance.image
        instance.slug = validated_data.get('slug') or slugify(instance.title)
        instance.status = validated_data.get('status') or instance.status
        instance.category = validated_data.get('add_category') or instance.category
        instance.author = validated_data.get('author') or instance.author
        instance.save()
        
        cleaned_tags = validated_data.get('add_tags')
        if cleaned_tags:
            instance.tags.clear()

            for cleaned_tag in cleaned_tags:
                tag = Tags.objects.get(title=cleaned_tag.title)
                instance.tags.add(tag)
                
        instance.save()
        return instance
        
    
    def get_comments(self, obj):
        serializer = CommentSerializer(list(obj.comments.all()), many=True)
        
        return serializer.data
        
        