from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from . import views

app_name = "comments"

router = DefaultRouter()
router.register(r'', views.CommentViewSet, basename='comment')

urlpatterns = router.urls