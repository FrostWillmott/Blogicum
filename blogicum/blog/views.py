from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
# from django.shortcuts import render

from django import forms
from django.utils import timezone
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404

from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.contrib.auth.models import User

from .forms import PostForm, CommentForm
from .models import Post, Category, Comment
from django.views.generic import (
    CreateView, DetailView, ListView, UpdateView, DeleteView
)

"""Views about User Profile"""


class ProfileView(TemplateView):
    template_name = 'blog/profile.html'

    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = get_object_or_404(User, username=self.kwargs[
            'username'])
        posts = Post.objects.filter(author=profile_user).annotate(
            comment_count=Count('comments')).order_by('-pub_date')
        paginator = Paginator(posts, 10)  # 10 публикаций на страницу
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['categories'] = Category.objects.all()
        context['profile'] = profile_user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    model = User
    fields = ['first_name', 'last_name', 'email']
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return filter_posts().annotate(comment_count=Count('comments'))

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})


"""Views about showing Posts"""


# NUMBER_OF_POSTS = 5

#
def filter_posts():
    return Post.objects.select_related(
        'author', 'location', 'category').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    # def get_queryset(self):
    #     return Post.objects.filter(is_published=True,
    #                                category__is_published=True,
    #                                pub_date__lte=timezone.now())
    def get_queryset(self):
        return filter_posts().annotate(comment_count=Count('comments'))
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['categories'] = Category.objects.all()
    #     return context


# def index(request):
#     template = 'blog/index.html'
#     # posts = filter_posts()[:NUMBER_OF_POSTS]
#     # context = {'post_list': posts}
#     # return render(request, template, context)
#     posts_list = Post.objects.all()
#     paginator = Paginator(posts_list, 10)  # 10 публикаций на страницу
#
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context = {'page_obj': page_obj}
#
#     return render(request, template, context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    # def post_detail(request, id):
    #     template = 'blog/detail.html'
    #     post = get_object_or_404(
    #         filter_posts(),
    #         id=id)
    #     context = {'post': post}
    #     return render(request, template, context)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class CategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'category_list'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug)
        if not category.is_published:
            raise Http404("Category not found")
        return filter_posts().filter(category__slug=category_slug)


# def category_posts(request, category_slug):
#     template = 'blog/category.html'
#     # category = get_object_or_404(
#     #     Category, slug=category_slug,
#     #     is_published=True)
#     # post_cat = filter_posts().filter(category=category)
#     # context = {'category': category, 'post_list': post_cat}
#     # return render(request, template, context)
#     category_posts = Post.objects.filter(category__slug=category_slug)
#     paginator = Paginator(category_posts,
#                           10)  # 10 публикаций на страницу
#
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context = {'page_obj': page_obj}
#
#     return render(request, template, context)

# @login_required
# def profile(request, username):
#     template = 'blog/profile.html'
#     # user = get_object_or_404(User, username=username)
#     # posts = Post.objects.filter(author=user)
#     # is_owner = request.user == user
#     # return render(request, 'profile.html',
#     #               {'user': user, 'posts': posts, 'is_owner': is_owner})
#     user_posts = Post.objects.filter(author__username=username)
#     paginator = Paginator(user_posts, 10)  # 10 публикаций на страницу
#
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context = {'page_obj': page_obj, 'profile': request.user}
#
#     return render(request, template, context)


"""Views about changing Posts"""


class CreatePostView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    # success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    # def form_valid(self, form):
    #     post = form.save(commit=False)
    #     post.author = self.request.user
    #     post.location = form.cleaned_data['location']
    #     post.category = form.cleaned_data['category']
    #     post.save()
    #     return super().form_valid(form)
    #
    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})
    #
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs


class EditPostView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    # def dispatch(self, *args, **kwargs):
    #     self.post = get_object_or_404(Post, id=self.kwargs['post_id'])
    #     if self.post.author != self.request.user:
    #         return HttpResponseRedirect(
    #             reverse('blog:post_detail', args=[self.post.id]))
    #     return super().dispatch(*args, **kwargs)
    #
    # def get_initial(self):
    #     initial = super().get_initial()
    #     initial.update({
    #         'title': self.post.title,
    #         'text': self.post.text,
    #         'location': self.post.location,
    #         'category': self.post.category,
    #     })
    #     return initial

    # def form_valid(self, form):
    #     self.post.title = form.cleaned_data['title']
    #     self.post.text = form.cleaned_data['text']
    #     self.post.location = form.cleaned_data['location']
    #     self.post.category = form.cleaned_data['category']
    #     self.post.save()
    #     return HttpResponseRedirect(
    #         reverse('blog:post_detail', args=[self.post.id]))

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['pk'] = self.post.id
    #     return kwargs
    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'id': self.object.id})


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    # context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    # def get_success_url(self):
    #     return reverse_lazy('blog:profile', kwargs={
    #         'username': self.request.user.username})
    #
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(author=self.request.user)
    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        class DummyForm(forms.ModelForm):
            class Meta:
                model = Post
                fields = []

        context['form'] = DummyForm(instance=post)
        return context


"""Views about Comments"""


class CreateCommentView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Comment
    form_class = CommentForm

    # success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs[
            'post_id'])
        return super().form_valid(form)

    # def form_valid(self, form):
    #     post = form.save(commit=False)
    #     post.author = self.request.user
    #     post.location = form.cleaned_data['location']
    #     post.category = form.cleaned_data['category']
    #     post.save()
    #     return super().form_valid(form)
    #
    # def get_success_url(self):
    #     return reverse('blog:profile',
    #                    kwargs={'username': self.request.user.username})

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})

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
                            kwargs={'pk': self.kwargs['post_id']})

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(author=self.request.user)


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
                            kwargs={'pk': self.kwargs['post_id']})
