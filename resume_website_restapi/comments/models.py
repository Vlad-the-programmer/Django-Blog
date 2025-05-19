from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    slug = models.SlugField(unique=True, 
                            max_length=100,
                            blank=True, 
                            null=True,
                            validators=[
                                  MaxLengthValidator(
                                    limit_value=100,
                                    message="Slug is over 100 letters long!"
                                    )
                                ])
    title = models.CharField(max_length=100,
                             blank=True, 
                             null=True,
                             validators=[
                                  MaxLengthValidator(
                                    limit_value=100,
                                    message="Title is over 100 letters long!"
                                    )
                                ])
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='comments',
                               on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post',
                             related_name='comments',
                             on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    content = models.TextField(max_length=500, blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to='comments')
    
    class Meta:
        verbose_name = _("Comments")
        verbose_name_plural = _("Comments")
        ordering = ['-date_created']
        
    def __str__(self):
        return self.title or ''
    
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return 
        
        
    def get_absolute_url(self):
        return reverse('posts:post-detail', kwargs={'slug': self.post.slug})
    
    
    
    
    