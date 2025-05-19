from .models import Category

def all_categories_to_every_template(request):
    categories = Category.objects.all()
    return dict(categories=categories)