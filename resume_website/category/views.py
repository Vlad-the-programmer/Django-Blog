from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.contrib import messages
# Permissions
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
# Generic class-based views
from django.views.generic.list import ListView
from django.views.generic.edit import (
                                        CreateView,
                                        UpdateView,
                                        DeleteView,
                                    )
# Pagination and searching by title
from .utils import searchCategoryPosts_title, paginatePosts

from posts.models import Post
from posts.utils import postsFilter
from .models import Category
from .forms import CategoryUpdateCreateForm


class CategoryPostsList(ListView):
    context_object_name = 'posts'
    template_name = 'index.html'
    
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug', '')
        try:
            queryset = Post.objects.filter(category__slug__exact=category_slug).distinct()
        except Post.DoesNotExist:
            queryset = None
            
        return queryset
    
    
    def get(self, request, *args, **kwargs):
        self.request = request
        return super().get(request, *args, **kwargs)
    
    
    def get_context_data(self, **kwargs):
        category_posts = self.get_queryset()
        if category_posts is not None:
            context = super().get_context_data(**kwargs) 
            
            # Context when posts is not filtered
            posts = category_posts
            _ , context['filter'] = postsFilter(self.request, posts)
            custom_range, page_obj = paginatePosts(self.request, posts, 5)
            
            # Get a category_slug for the search form in index.html
            category_slug = self.request.path.split('/')[2]
            
            # Search query and filtered posts
            if self.request.GET:
                if self.request.GET.get('search_query'):
                    
                    posts, search_query = searchCategoryPosts_title(
                                                            self.request, 
                                                            posts,
                                                            category_slug=category_slug
                                                        )
                    _ , page_obj = paginatePosts(self.request, posts, 5)

                    context['search_query'] = search_query
                    
                else:
                    posts, _ = postsFilter(self.request, category_posts)
                    _ , page_obj = paginatePosts(self.request, posts, 5)
                    
            
            context['page_obj'] = page_obj
            context['category_slug'] = category_slug
            context['custom_range'] = custom_range
            context['posts'] = posts
            print('Context', context)
            
        return context
     

@method_decorator(permission_required("category.add", raise_exception=True), name='dispatch')       
class CategoryCreateView(CreateView):
    model = Category
    template_name = 'categories/category-create.html'
    form_class = CategoryUpdateCreateForm
    success_url = reverse_lazy('posts:posts-list')
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            if not category.slug:
                category.slug = slugify(category.title)
            else:
                category.slug.lower()
            category.save()
            messages.success(request, 'Created!')
            
            return redirect(self.success_url)
        
        messages.success(request, 'Invalid data!')
        return redirect(reverse_lazy('category:category-create'))
    

@method_decorator(permission_required("category.edit", raise_exception=True), name='dispatch')       
class CategoryUpdateView(UpdateView):
    template_name = 'categories/category-create.html'
    form_class = CategoryUpdateCreateForm
    success_url = reverse_lazy('posts:posts-list')
    
    
    def get_object(self):
        category_slug = self.kwargs.get('category_slug', '')
        try:
            category = Category.objects.get_or_create(slug=category_slug)
        except Category.DoesNotExist:
            category = None
            
        return category
    
    
    def post(self, request, *args, **kwargs):
        category = self.get_object()
        form = self.form_class(instance=category, data=request.POST)
        print(form.errors)
        if form.is_valid() and category is not None:
            category = form.save(commit=False)
            category.slug.lower()
            category.title.lower()
            
            category.save()
            messages.success(request, 'Updated!')
            return redirect(self.success_url)
        else:
            context = {}
            context['form'] = self.form_class
            messages.error(request, 'Invalid data!')

        return render(request, self.template_name, context)


@method_decorator(permission_required("category.delete", raise_exception=True), name='dispatch')       
class CategoryDeleteView(DeleteView):
    template_name = 'categories/category-delete.html'
    success_url = reverse_lazy('posts:posts-list')
    
    def get_object(self):
        category_slug = self.kwargs.get('category_slug', '')
        try:
            object = get_object_or_404(Category, slug=category_slug)
        except Category.DoesNotExist:
            object = None
            
        return object
    
    def form_valid(self, form):
        messages.success(self.request, 'Deleted!')
        return super().form_valid(form)
        
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid data!')
        return super().form_invalid(form)
    