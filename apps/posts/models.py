from django.db import models

from ..accounts.models import Author


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "tags"

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="posts"
    )
    tags = models.ManyToManyField("Tag", related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        db_table = "posts"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
