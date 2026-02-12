from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models


class User(AbstractUser):
    avatar = models.FileField(
        upload_to='avatars/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
    )

    def display_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
