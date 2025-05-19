from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    # id = models.UUIDField(default=uuid.uuid4, unique=True,
    #                       primary_key=True, editable=False)
    title = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.slug or self.title
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

