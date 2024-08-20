from django.urls import path
from django.urls.conf import include

from . import views
from .views import (
    CreatePostView, ProfileView, EditPostView,
    DeletePostView, ProfileEditView,
    PostDetailView, IndexView, CategoryView,
    CreateCommentView, EditCommentView, DeleteCommentView
)

app_name = 'blog'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('', IndexView.as_view(), name='index'),
    path('posts/<int:pk>/', PostDetailView.as_view(),
         name='post_detail'),
    path('category/<slug:category_slug>/', CategoryView.as_view(),
         name='category_posts'),
    path('posts/create/', CreatePostView.as_view(),
         name='create_post'),
    path('profile/<str:username>/', ProfileView.as_view(),
         name='profile'),
    path('posts/<int:post_id>/edit/', EditPostView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/', DeletePostView.as_view(),
         name='delete_post'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         DeleteCommentView.as_view(), name='delete_comment'),
    path("profile/<slug:username>/edit/", ProfileEditView.as_view(),
         name="edit_profile"),
    path(" posts/<post_id>/comment/", CreateCommentView.as_view(),
         name="add_comment"),
    path("posts/<post_id>/edit_comment/<comment_id>/",
         EditCommentView.as_view(), name="edit_comment"),
    # path("posts/<post_id>/delete_comment/<comment_id>/",
    #      DeleteCommentView.as_view(), name="delete_comment"),
]
