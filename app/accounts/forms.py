"""Django Forms for accounts App"""
from __future__ import unicode_literals

from django.contrib.auth.forms import AuthenticationForm

from accounts.exceptions import PermissionDenied


class UserLoginForm(AuthenticationForm):
    """
    Form to login a user
    """

    def __init__(self, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        super(UserLoginForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        self.fields['username'].help_text = 'Email'

    def clean(self):
        """Clean form"""
        super(UserLoginForm, self).clean()
        user = self.get_user()
        if not user.is_staff:
            raise PermissionDenied()
