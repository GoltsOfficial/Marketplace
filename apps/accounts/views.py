from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


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


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Author, Profile
from .forms import UserForm, ProfileForm


@login_required
def profile_view(request):
    author, _ = Author.objects.get_or_create(user=request.user)
    profile, _ = Profile.objects.get_or_create(author=author)
    return render(request, "accounts/profile.html", {"profile": profile})


@login_required
def profile_edit(request):
    author, _ = Author.objects.get_or_create(user=request.user)
    profile, _ = Profile.objects.get_or_create(author=author)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("accounts:profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(request, "accounts/profile_edit.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })
