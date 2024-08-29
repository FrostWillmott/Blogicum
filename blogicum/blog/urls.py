from django.urls import path
from django.urls.conf import include

from .views import (
    CreatePostView, EditPostView,
    DeletePostView, PostDetailView,
    IndexView, CategoryView, CreateCommentView,
    EditCommentView, DeleteCommentView, ProfileView, ProfileEditView)

app_name = 'blog'

post_urls = [
    path('<int:post_id>/', PostDetailView.as_view(),
         name='post_detail'),
    path('create/', CreatePostView.as_view(),
         name='create_post'),
    path('<int:post_id>/edit/', EditPostView.as_view(),
         name='edit_post'),
    path('<int:post_id>/delete/', DeletePostView.as_view(),
         name='delete_post'),
    path('<int:post_id>/delete_comment/<int:comment_id>/',
         DeleteCommentView.as_view(), name='delete_comment'),
    path("<int:post_id>/comment/", CreateCommentView.as_view(),
         name="add_comment"),
    path("<int:post_id>/edit_comment/<comment_id>/",
         EditCommentView.as_view(), name="edit_comment"),
]

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('posts/', include(post_urls)),
    path('category/<slug:category_slug>/', CategoryView.as_view(),
         name='category_posts'),
    path('profile/<str:username>/', ProfileView.as_view(),
         name='profile'),
    path("profile/<slug:username>/edit/", ProfileEditView.as_view(),
         name="edit_profile"),
]
