from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Users(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('borrower', 'Borrower'),
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='borrower')
    max_borrowed_book = models.CharField(default=1)
    groups = models.ManyToManyField(Group, related_name='users_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='users_permissions_set', blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

