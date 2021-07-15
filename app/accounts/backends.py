"""
Django backends overwriting behavior
"""
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone

from django.utils.translation import ugettext_lazy as _
from accounts import models

INVALID_AUTH = _('The authentication field is not a valid email.')


class EmailBackend(ModelBackend):
    """
    Check if email works
    """

    def __init__(self):
        super(EmailBackend, self).__init__()
        self.user_model = models.User

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticating by email as username
        :param request: the request instance
        :param username: identification to authenticate
        :param password: password for you account
        :return: Return the authenticated user or None
        """

        try:
            user = self.user_model.objects.get(**{'email': username})
        except self.user_model.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            self.user_model().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        return None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have that attribute are allowed.
        """
        valid_date = user.jwt_valid_after < timezone.now()
        return valid_date and super(EmailBackend, self).user_can_authenticate(user)
