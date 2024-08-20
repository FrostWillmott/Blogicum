from django.urls import path

from . import views
from .views import (
    register, AboutView, RulesView)

app_name = 'pages'

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    path('rules/', RulesView.as_view(), name='rules'),
    path('auth/registration/', register, name='registration'),
    # path('profile/<str:username>/', profile, name='profile'),
    # path('profile/<str:username>/', ProfileView.as_view(),
    #      name='profile'),
    # path("profile/<slug:username>/edit/", ProfileEditView.as_view(),
    #      name="edit_profile"),
]

handler500 = 'pages.views.custom_500_error'
handler404 = 'pages.views.custom_404_error'
handler403 = 'pages.views.csrf_failure'
