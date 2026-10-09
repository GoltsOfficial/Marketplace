from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Author, Profile


def login_view(request):
    if request.user.is_authenticated:
        return redirect("posts:post_list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect("posts:post_list")
        messages.error(request, "Неверный логин или пароль.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("posts:post_list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаём Author и Profile
            author = Author.objects.create(name=user.username)
            Profile.objects.create(author=author, bio="")
            login(request, user)
            messages.success(request, "Регистрация успешна!")
            return redirect("posts:post_list")
        messages.error(request, "Ошибка регистрации. Проверьте данные.")
    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("posts:post_list")


@login_required
def profile_view(request):
    try:
        author = Author.objects.get(name=request.user.username)
        profile = getattr(author, "profile", None)
    except Author.DoesNotExist:
        author = None
        profile = None

    return render(request, "accounts/profile.html", {
        "author": author,
        "profile": profile,
        "user": request.user,
    })
