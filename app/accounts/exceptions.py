"""
To manage exceptions.
"""
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from api.utils.exceptions import BaseError


class PermissionDenied(BaseError):
    """Exception for permission denied. This exception must be used when a user does not have access to a resource"""

    message = _('Permission denied.')
    code = 'permission-denied'


class LoginRequired(BaseError):
    """
    Exception for login required. This exception must be used when a non authenticated user is trying to access to
    a private resource
    """

    message = _('Login required.')
    code = 'login-required'
