from django.db import models
from django.core.validators import MaxLengthValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    title = models.CharField(max_length=100,
                             blank=True, 
                             null=True,
                             validators=[
                                  MaxLengthValidator(
                                    limit_value=100,
                                    message="Title is over 100 letters long!"
                                    )
                                ])
    author = models.ForeignKey('users.Profile',
                               related_name='comments',
                               on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post',
                             related_name='comment',
                             on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    content = models.TextField(max_length=500, blank=True, null=True)
    image = models.ImageField(  
                              null=True, 
                              blank=True, 
                              upload_to=f'comments/{date_created}'
                              )
    
    
    class Meta:
        verbose_name = _("Comments")
        verbose_name_plural = _("Comments")
        ordering = ['-date_created']
        
    def __str__(self):
        return self.title
    
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return 
        
        
    def get_absolute_url(self):
        return reverse('posts:post-detail', kwargs={'slug': self.post.slug})
    
    
    