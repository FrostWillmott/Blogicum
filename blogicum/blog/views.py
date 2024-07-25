from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Post, Category

NUMBER_OF_POSTS = 5


def filter_posts():
    return Post.objects.select_related(
        'author', 'location', 'category').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def index(request):
    template = 'blog/index.html'
    posts = filter_posts()[:NUMBER_OF_POSTS]
    context = {'post_list': posts}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        filter_posts(),
        id=id)
    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category, slug=category_slug,
        is_published=True)
    post_cat = filter_posts().filter(category=category)
    context = {'category': category, 'post_list': post_cat}
    return render(request, template, context)
