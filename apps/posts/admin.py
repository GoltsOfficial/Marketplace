from django.contrib import admin

from .models import Post, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "is_published")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "body")
    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    search_fields = ("name",)
    list_editable = ("name",)
