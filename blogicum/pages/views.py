from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required


def about(request):
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    template = 'pages/rules.html'
    return render(request, template)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 404 мы не станем.
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    # Переменная exception содержит отладочную информатцию;
    # выводить её в шаблон пользовательской страницы 403 мы не станем.
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('login'))
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration.html',
                  {'form': form})


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    # Здесь добавьте логику для получения публикаций пользователя
    return render(request, 'profile.html', {'user': user})
