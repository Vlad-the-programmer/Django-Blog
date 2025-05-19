from django import forms
from .models import Category

class CategoryUpdateCreateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('title', 'slug')