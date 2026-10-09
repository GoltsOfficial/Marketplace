from django.db import models


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class Profile(models.Model):
    author = models.OneToOneField(
        Author, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField()
