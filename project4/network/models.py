from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", blank=True, related_name="followers")


class Post(models.Model):
    text = models.CharField(max_length=280)
    creation_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likes = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"{self.text} created by: {self.user} at: {self.creation_time}"
