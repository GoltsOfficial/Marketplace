from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.urls import reverse

from .forms import RegisterForm, UserForm, ProfileForm
from .models import Author, Profile


def login_view(request):
    if request.user.is_authenticated:
        return redirect("posts:post_list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(
                    request,
                    "Аккаунт не активирован. Проверьте email и перейдите по ссылке подтверждения.",
                )
                return render(request, "accounts/login.html", {"form": form})
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
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Author + Profile
            author = Author.objects.create(user=user, name=user.username)
            Profile.objects.create(author=author)

            # Письмо подтверждения
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            confirm_url = request.build_absolute_uri(
                reverse("accounts:confirm_email", kwargs={"uidb64": uid, "token": token})
            )
            subject = "Подтверждение email — Marketplace"
            message = render_to_string(
                "accounts/email_confirm.txt",
                {"user": user, "confirm_url": confirm_url},
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(
                request,
                "Регистрация почти готова! Проверьте почту и перейдите по ссылке для подтверждения email.",
            )
            return redirect("accounts:login")
        messages.error(request, "Ошибка регистрации. Проверьте данные.")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        messages.success(request, "Email успешно подтверждён! Теперь можно войти.")
        return redirect("accounts:login")

    messages.error(request, "Ссылка подтверждения недействительна или устарела.")
    return redirect("accounts:login")


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("posts:post_list")


@login_required
def profile_view(request):
    author, _ = Author.objects.get_or_create(
        user=request.user,
        defaults={"name": request.user.username},
    )
    profile, _ = Profile.objects.get_or_create(author=author)
    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "user": request.user,
            "email_confirmed": request.user.is_active,
        },
    )


@login_required
def profile_edit(request):
    author, _ = Author.objects.get_or_create(
        user=request.user,
        defaults={"name": request.user.username},
    )
    profile, _ = Profile.objects.get_or_create(author=author)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # Обновляем имя автора, если нужно
            if author.name != request.user.username:
                author.name = request.user.username
                author.save(update_fields=["name"])
            messages.success(request, "Профиль сохранён.")
            return redirect("accounts:profile")
        messages.error(request, "Исправьте ошибки в форме.")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )


@login_required
def resend_confirmation(request):
    """Повторная отправка письма подтверждения."""
    user = request.user
    if user.is_active:
        messages.info(request, "Email уже подтверждён.")
        return redirect("accounts:profile")

    if not user.email:
        messages.error(request, "Укажите email в профиле.")
        return redirect("accounts:profile_edit")

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    confirm_url = request.build_absolute_uri(
        reverse("accounts:confirm_email", kwargs={"uidb64": uid, "token": token})
    )
    subject = "Подтверждение email — Marketplace"
    message = render_to_string(
        "accounts/email_confirm.txt",
        {"user": user, "confirm_url": confirm_url},
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    messages.success(request, "Письмо с подтверждением отправлено повторно.")
    return redirect("accounts:profile")
