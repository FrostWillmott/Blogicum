# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.shortcuts import render
# from django.urls import reverse
# from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


# from django.contrib.auth.forms import UserCreationForm


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def custom_500_error(request):
    return render(request, 'pages/500.html', status=500)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
