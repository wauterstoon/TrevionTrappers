from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.URLField(blank=True)

    def display_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
