# -*- coding: utf-8 -*-
"""
Models of accounts app
"""
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from accounts import validators


class User(AbstractBaseUser, PermissionsMixin):
    """
    Model to handle users specs.
    """

    email = models.EmailField(unique=True, null=True, blank=True, validators=[validators.CONFUSABLE_VALIDATE_EMAIL],
                              help_text='Email field')
    fullname = models.CharField(max_length=50, help_text='User fullname')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text='To inability a user')

    joined = models.DateTimeField(auto_now_add=True)
    jwt_valid_after = models.DateTimeField(auto_now_add=True)

    # using email field as default username.
    USERNAME_FIELD = 'email'

    def reset_jwt_valid_after(self):
        """Reset jwt_valid_after field"""
        self.jwt_valid_after = timezone.now()
        self.save()

    def __str__(self):
        return self.email
