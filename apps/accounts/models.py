from django.conf import settings
from django.db import models


class Author(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name or (self.user.username if self.user else str(self.pk))


class Profile(models.Model):
    author = models.OneToOneField(
        Author, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField("О себе", blank=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    city = models.CharField("Город", max_length=100, blank=True)
    birth_date = models.DateField("Дата рождения", blank=True, null=True)
    email_confirmed = models.BooleanField("Email подтверждён", default=False)
    last_confirm_email_sent = models.DateTimeField(
        "Последняя отправка подтверждения", null=True, blank=True
    )

    def __str__(self):
        return f"Профиль {self.author}"
