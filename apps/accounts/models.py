from django.db import models


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class Profile(models.Model):
    author = models.OneToOneField(
        Author, on_delete=models.CASCADE, related_name="profile"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField("About me", blank=True)
    phone = models.CharField("Phone number", max_length=20, blank=True)
    city = models.CharField("City", max_length=100, blank=True)
    birth_date = models.DateField("Birth date", blank=True, null=True)

    def __str__(self):
        return f"{self.author} Profile"
