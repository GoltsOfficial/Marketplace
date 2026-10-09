from django.contrib import admin

from .models import Author, Profile


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    list_filter = ("name",)
    search_fields = ("name",)
    list_editable = ("name",)



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("author", "bio")
    list_filter = ("author",)
    search_fields = ("author", "bio")


