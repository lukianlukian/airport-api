from django.contrib.auth.models import AbstractUser
from django.db import models
from user.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    groups = models.ManyToManyField(
        "auth.Group", related_name="airport_user_set", blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="airport_user_set", blank=True
    )

    def __str__(self):
        return self.email
