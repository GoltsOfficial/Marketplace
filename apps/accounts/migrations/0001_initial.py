import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="author",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bio", models.TextField(blank=True, verbose_name="О себе")),
                ("phone", models.CharField(blank=True, max_length=20, verbose_name="Телефон")),
                ("city", models.CharField(blank=True, max_length=100, verbose_name="Город")),
                ("birth_date", models.DateField(blank=True, null=True, verbose_name="Дата рождения")),
                ("email_confirmed", models.BooleanField(default=False, verbose_name="Email подтверждён")),
                (
                    "last_confirm_email_sent",
                    models.DateTimeField(blank=True, null=True, verbose_name="Последняя отправка подтверждения"),
                ),
                (
                    "author",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to="accounts.author",
                    ),
                ),
            ],
        ),
    ]
