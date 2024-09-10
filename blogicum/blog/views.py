from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin
)
from django.db.models import Count
from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.conf import settings

from .forms import PostForm, CommentForm
from .models import Post, Category, Comment
from django.views.generic import (
    CreateView, DetailView, ListView, UpdateView, DeleteView
)


class ProfileView(ListView):
    """View to display a user's profile with their posts."""

    # model = Post
    template_name = 'blog/profile.html'
    # context_object_name = 'post_list'
    paginate_by = settings.PAGIN_SIZE

    def get_user_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        profile_user = self.get_user_object()
        queryset = get_posts_queryset(
            filter_param=self.request.user != profile_user,
            annotate_param=True).filter(author=profile_user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user_object()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """View to edit the profile of the logged-in user."""

    template_name = 'blog/user.html'
    model = User
    fields = ['first_name', 'last_name', 'email']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


def get_posts_queryset(filter_param=False, annotate_param=False):
    queryset = Post.objects.select_related(
        'author', 'category', 'location')
    if filter_param:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    if annotate_param:
        queryset = queryset.annotate(
            comment_count=Count('comments')).order_by('-pub_date')
    return queryset


class IndexView(ListView):
    """View to display the index page with a list of posts."""

    # model = Post
    template_name = 'blog/index.html'
    # context_object_name = 'post_list'
    paginate_by = settings.PAGIN_SIZE
    queryset = get_posts_queryset(filter_param=True, annotate_param=True)


class PostDetailView(DetailView):
    """View to display the details of a single post."""

    # model = Post
    template_name = 'blog/detail.html'
    # context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    queryset = get_posts_queryset(filter_param=False,
                                  annotate_param=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author')
        return context

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user and (
                post.pub_date > timezone.now()
                or post.is_published is False
                or post.category.is_published is False):
            raise Http404("Нет прав на просмотр")
        return post


class CategoryView(ListView):
    """View to display posts of a specific category."""

    template_name = 'blog/category.html'
    # context_object_name = 'category_list'
    paginate_by = settings.PAGIN_SIZE

    def get_category_object(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs.get('category_slug'),
            is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category_object()
        return context

    def get_queryset(self):
        category = self.get_category_object()
        return get_posts_queryset(filter_param=True,
                                  annotate_param=True
                                  ).filter(category=category)


class CreatePostView(LoginRequiredMixin, CreateView):
    """View to create a new post."""

    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostViewMixin(UserPassesTestMixin):
    """Mixin for views that edit or delete posts"""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)


class EditPostView(LoginRequiredMixin, PostViewMixin, UpdateView):
    """View to edit an existing post."""

    form_class = PostForm

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.id})


class DeletePostView(LoginRequiredMixin, PostViewMixin, DeleteView):
    """View to delete an existing post."""

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        context['form'] = PostForm(instance=post)
        return context


class CreateCommentView(LoginRequiredMixin, CreateView):
    """View to create a new comment on a post."""

    template_name = 'blog/create.html'
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if not post.is_published and post.author != request.user:
            raise Http404("Only the author can comment on unpublished posts.")
        return super().dispatch(request, *args, **kwargs)

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


class CommentViewMixin(UserPassesTestMixin):
    """Mixin for views that edit or delete comments"""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def handle_no_permission(self):
        comment = self.get_object()
        return redirect('blog:post_detail',
                        post_id=comment.post.id)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class DeleteCommentView(LoginRequiredMixin, CommentViewMixin, DeleteView):
    """View to delete an existing comment."""

    pass


class EditCommentView(LoginRequiredMixin, CommentViewMixin, UpdateView):
    """View to edit an existing comment."""

    form_class = CommentForm
