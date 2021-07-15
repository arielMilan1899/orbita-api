# -*- coding: utf-8 -*-
"""
Helper to validate form data
"""
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.validators import validate_email, RegexValidator
from django.utils.deconstruct import deconstructible

from confusable_homoglyphs import confusables

CONFUSABLE_EMAIL = _('This email address cannot be registered. '
                     'Please supply a different email address.')
INVALID_PHONE = _('The phone number is invalid.')


@deconstructible
class ConfusableEmailValidator:
    """Check confusable emails"""

    def __call__(self, value):
        self.validate_confusables_email(value)

    @staticmethod
    def validate_confusables_email(value):
        """
        Validator which disallows 'dangerous' email addresses likely to
        represent homograph attacks.
        An email address is 'dangerous' if either the local-part or the
        domain, considered on their own, are mixed-script and contain one
        or more characters appearing in the Unicode Visually Confusable
        Characters file.
        """
        if '@' not in value:
            return
        local_part, domain = value.split('@')
        if confusables.is_dangerous(local_part) or \
                confusables.is_dangerous(domain):
            raise ValidationError({'email': CONFUSABLE_EMAIL}, code='invalid')


CONFUSABLE_VALIDATE_EMAIL = ConfusableEmailValidator()

VALIDATE_PHONE = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=INVALID_PHONE)


def is_email(email):
    """
    Using django email validator. It can be configure to raise a specific message
    and code_error when the email is not valid.
    :param email: email address
    :return: Boolean describing if the email is syntactically correct.
    """
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
