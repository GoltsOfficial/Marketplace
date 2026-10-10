from django.contrib import admin

from .models import Author, Profile


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user")
    list_filter = ("name",)
    search_fields = ("name", "user__username", "user__email")
    raw_id_fields = ("user",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("author", "phone", "city")
    search_fields = ("author__name", "author__user__username", "phone", "city")
