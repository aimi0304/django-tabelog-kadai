from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.AutoField(
        primary_key=True,
        verbose_name='ID'
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name='有料会員'
    )
    birthday = models.DateField(
        blank=True,
        null=True,
        verbose_name='誕生日'
    )
    gender = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='性別'
    )
