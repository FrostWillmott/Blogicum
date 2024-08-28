from django import forms

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.utils import timezone
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.conf import settings

from .forms import PostForm, CommentForm
from .models import Post, Category, Comment
from django.views.generic import (
    CreateView, DetailView, ListView, UpdateView, DeleteView
)


"""Views about User Profile"""

class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'post_list'
    paginate_by = settings.PAGIN_SIZE

    def get_queryset(self):
        profile_user = get_object_or_404(User, username=self.kwargs[
            'username'])
        return Post.objects.filter(author=profile_user).annotate(
            comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User,
                                               username=self.kwargs[
                                                   'username'])
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    model = User
    fields = ['first_name', 'last_name', 'email']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})


"""Views about showing Posts"""


def filter_posts():
    return Post.objects.select_related(
        'author', 'location', 'category').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')

# def filter_post(first_param=False, second_param=False):
#     queary_set = Post.objects.select_related(
#         'author', 'location', 'category')
#     if first_param:
#         queary_set = queary_set.filter(pub_date__lte=timezone.now())
#     if second_param:
#         queary_set = queary_set.filter(is_published=True).annotate(
#             comment_count=Count('comments')).order_by('-pub_date')
#     return queary_set


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = settings.PAGIN_SIZE

    def get_queryset(self):
        return filter_posts().annotate(comment_count=Count('comments'))


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if not post.is_published and post.author != self.request.user:
            raise Http404("Нет прав на просмотр")
        return post


class CategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'category_list'
    paginate_by = settings.PAGIN_SIZE

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug)
        if not category.is_published:
            raise Http404("Category not found")
        return filter_posts().filter(category__slug=category_slug)


"""Views about changing Posts"""


class CreatePostView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm


    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

class EditPostView(UserPassesTestMixin, UpdateView):

    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if not request.user.is_authenticated:
            return redirect('/auth/login/')
        if post.author != self.request.user:
            return redirect('blog:post_detail',
                            post_id=post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.id})


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        context['form'] = PostForm(instance=post)
        return context


"""Views about Comments"""


class CreateCommentView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs[
            'post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context


class EditCommentView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise PermissionDenied(
                "Вы не можете менять чужие комментарии.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if (comment.author != self.request.user
                and not self.request.user.is_staff):
            raise PermissionDenied(
                "Вы не можете удалять чужие комментарии.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})
