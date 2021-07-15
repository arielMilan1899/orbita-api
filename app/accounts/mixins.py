"""
Classes to be used as helpers to the account logic.
"""
from __future__ import unicode_literals
from api.utils.decorators import login_required


class LoginRequiredMutation:
    """
    Mixin to require user login mutation.
    Use this mixin with any mutation class.
    """

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input_fields):
        """
        Mutate method required for a mutation.
        """
        return super(LoginRequiredMutation, cls).mutate_and_get_payload(root, info, **input_fields)


class WithUserLoggedForm:
    """
    Mixin to require user login mutation.
    Use this mixin with any mutation class.
    """

    def __init__(self, *args, **kwargs):
        super(WithUserLoggedForm, self).__init__(*args, **kwargs)
        self._user = None

    @property
    def user(self):
        """
        User instance getter.
        """
        return self._user

    @user.setter
    def user(self, user):
        """
        User instance setter.
        """
        self._user = user
