from django.urls import path

from . import views
from .views import register, profile

app_name = 'pages'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('rules/', views.rules, name='rules'),
    path('auth/registration/', register, name='registration'),
    path('profile/<str:username>/', profile, name='profile'),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
