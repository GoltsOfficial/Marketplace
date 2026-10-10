from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.urls import reverse

from .forms import RegisterForm, UserForm, ProfileForm
from .models import Author, Profile

RESEND_COOLDOWN = timedelta(minutes=5)


def _send_confirm_email(request, user):
    """Отправка письма подтверждения на указанный email."""
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


def _get_or_create_profile(user):
    author, _ = Author.objects.get_or_create(
        user=user,
        defaults={"name": user.username},
    )
    profile, _ = Profile.objects.get_or_create(author=author)
    return author, profile


def _cooldown_remaining_seconds(profile):
    if not profile.last_confirm_email_sent:
        return 0
    elapsed = timezone.now() - profile.last_confirm_email_sent
    left = RESEND_COOLDOWN - elapsed
    if left.total_seconds() <= 0:
        return 0
    return int(left.total_seconds())


def login_view(request):
    if request.user.is_authenticated:
        return redirect("posts:post_list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Сначала обычная проверка
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect("posts:post_list")

        # Старые аккаунты с is_active=False — активируем и пускаем
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
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
            author = Author.objects.create(user=user, name=user.username)
            profile = Profile.objects.create(author=author, email_confirmed=False)

            try:
                _send_confirm_email(request, user)
                profile.last_confirm_email_sent = timezone.now()
                profile.save(update_fields=["last_confirm_email_sent"])
                messages.success(
                    request,
                    "Регистрация успешна! Письмо с подтверждением отправлено на email. "
                    "Вход уже доступен; публиковать объявления — после подтверждения.",
                )
            except Exception as e:
                messages.warning(
                    request,
                    f"Аккаунт создан, но письмо не отправилось: {e}. "
                    "Повторите отправку в профиле.",
                )

            login(request, user)
            return redirect("posts:post_list")
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
        _, profile = _get_or_create_profile(user)
        profile.email_confirmed = True
        profile.save(update_fields=["email_confirmed"])
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        messages.success(
            request,
            "Email успешно подтверждён! Теперь можно публиковать объявления.",
        )
        if request.user.is_authenticated:
            return redirect("accounts:profile")
        return redirect("accounts:login")

    messages.error(request, "Ссылка подтверждения недействительна или устарела.")
    return redirect("accounts:login")


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("posts:post_list")


@login_required
def profile_view(request):
    _, profile = _get_or_create_profile(request.user)
    cooldown_left = _cooldown_remaining_seconds(profile)
    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "user": request.user,
            "email_confirmed": profile.email_confirmed,
            "cooldown_left": cooldown_left,
        },
    )


@login_required
def profile_edit(request):
    author, profile = _get_or_create_profile(request.user)
    old_email = request.user.email

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            if request.user.email != old_email:
                profile.email_confirmed = False
                profile.save(update_fields=["email_confirmed"])
                try:
                    _send_confirm_email(request, request.user)
                    profile.last_confirm_email_sent = timezone.now()
                    profile.save(update_fields=["last_confirm_email_sent"])
                    messages.info(
                        request,
                        "Email изменён. На новый адрес отправлено письмо подтверждения.",
                    )
                except Exception:
                    messages.warning(
                        request,
                        "Email изменён, но письмо подтверждения не удалось отправить.",
                    )
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
    _, profile = _get_or_create_profile(request.user)

    if profile.email_confirmed:
        messages.info(request, "Email уже подтверждён.")
        return redirect("accounts:profile")

    if not request.user.email:
        messages.error(request, "Укажите email в профиле.")
        return redirect("accounts:profile_edit")

    left = _cooldown_remaining_seconds(profile)
    if left > 0:
        minutes = left // 60
        seconds = left % 60
        messages.warning(
            request,
            f"Повторная отправка будет доступна через {minutes}:{seconds:02d}.",
        )
        return redirect("accounts:profile")

    try:
        _send_confirm_email(request, request.user)
        profile.last_confirm_email_sent = timezone.now()
        profile.save(update_fields=["last_confirm_email_sent"])
        messages.success(request, "Письмо с подтверждением отправлено на ваш email.")
    except Exception as e:
        messages.error(request, f"Не удалось отправить письмо: {e}")

    return redirect("accounts:profile")
