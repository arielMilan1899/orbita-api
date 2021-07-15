"""
Accounts app definition
"""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # pragma: no cover

from django.apps import AppConfig  # pragma: no cover


class AccountsConfig(AppConfig):  # pragma: no cover
    """
    Accounts app config
    """
    name = 'accounts'

    def ready(self):
        super(AccountsConfig, self).ready()
