"""
To manage exceptions.
"""
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from api.utils.exceptions import BaseError


class CategoryDoesNotExist(BaseError):
    """
    Exception for non existent category. This exception must be used when we are trying to get an invalid
    ad (Category does not exist).
    """

    message = _('Category does not exist.')
    code = 'invalid-category'
