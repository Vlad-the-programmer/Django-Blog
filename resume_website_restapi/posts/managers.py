from django.db import models
from .choices import STATUS as STATUS_CHOICES


class PublishedPostsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            status=STATUS_CHOICES.PUBLISH,
            is_active=True
        )
    
    # This ensures the manager can be used for creating/updating objects too
    def create(self, **kwargs):
        # Default to published status if not specified
        if 'status' not in kwargs:
            kwargs['status'] = STATUS_CHOICES.PUBLISH
        return super().create(**kwargs)