"""
Customs functions decorators
"""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from accounts.exceptions import LoginRequired


def login_required(schema_func):
    """
    Check user is authenticated
    """

    # pylint: disable=C0111
    def wrap(cls, *args, **input_fields):
        info = args[1]
        if not info.context.user.is_authenticated:
            raise LoginRequired()

        return schema_func(cls, *args, **input_fields)

    wrap.__doc__ = schema_func.__doc__
    wrap.__name__ = schema_func.__name__
    return wrap
