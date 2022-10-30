from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = (
        ('user', 'Аутентифицированный пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=16, choices=ROLES, default='user')
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    confirmation_code = models.CharField(max_length=256)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    models.UniqueConstraint(fields=['username', 'email'],
                            name='unic_username_email_record')

    class Meta:
        ordering = ('username',)
