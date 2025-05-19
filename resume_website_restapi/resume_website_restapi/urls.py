
# DRF
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static  import static
from django.contrib import admin
from django.urls import path, include

# from users import views as custom_views

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('posts/',      include('posts.urls',    namespace='posts')),
    path('users/',      include('users.urls',    namespace='users')),
    path('comments/',   include('comments.urls', namespace='comments')),
    path('categories/', include('category.urls', namespace='category')),
    # path('auth/',     include('dj_rest_auth.urls')),
    path('accounts/',   include('allauth.urls')),
    
]

# # Router urls
# urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)