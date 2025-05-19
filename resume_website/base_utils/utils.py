from django.shortcuts import redirect
from django.urls import reverse_lazy


def check_is_admin(request):
    if not request.user.is_superuser:
        return redirect(reverse_lazy('posts:posts-list'))
    