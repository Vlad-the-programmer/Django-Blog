from .models import Profile

def template_context_processor(request, *args, **kwargs):
    user = request.user
    print(user)
    if user.is_authenticated:
        profile = Profile.objects.get(email=user.email)
        return {'user': user, 'profile': profile}
    else:
        return {'user': '', 'profile': ''}