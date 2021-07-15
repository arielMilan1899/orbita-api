"""
A middleware to extract the user from request
"""
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from jwt_auth.exceptions import AuthenticationFailed
from jwt_auth.utils import jwt_payload_handler
from jwt_auth.mixins import JSONWebTokenAuthMixin


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware for authenticating JSON Web Tokens in Authorize Header.
    If the token is valid, the user is going to be added to the request as request.user,
    otherwise it is set to AnonymousUser.
    Based on https://github.com/creimers/graphene-auth-examples/blob/master/src/apps/account/middleware.py.
    """

    def process_request(self, request):
        """
        Code to be executed for each request before the view (and later middleware) are called.
        :param request: the request
        :return: None
        """
        request.user = SimpleLazyObject(lambda: self.get_user_jwt(request))

    @staticmethod
    def get_user_jwt(request):
        """
        Replacement for django session auth get_user & auth.get_user JSON Web Token authentication.
        Inspects the token for the user_id, attempts to get that user from the DB
        and assigns the user on the request object. Otherwise it defaults to AnonymousUser.
        This will work with existing decorators like LoginRequired  ;)
        :param request: Middleware request.
        :return: instance of user object or AnonymousUser object.
        """
        try:
            user_jwt = JWTValidation().authenticate(request)
            # store the first part from the tuple (user, obj)
            user = user_jwt[0]
        except AuthenticationFailed:
            return AnonymousUser()

        return user


class JWTValidation(JSONWebTokenAuthMixin):
    """
    Check if the jwt is after a limit date.
    """

    def authenticate_credentials(self, payload):
        """
        Returns an user accepted by the default authentication workflow,
        only if the jwt was created after the user's jwt_valid_after.
        """
        user = super(JWTValidation, self).authenticate_credentials(payload)

        created = payload.get('iat')
        # If the date of the jwt is after the limit date saved in DB, the jwt is no valid.
        if not created or user.jwt_valid_after.replace(microsecond=0) > datetime.fromtimestamp(created, timezone.utc):
            msg = 'Invalid jwt'
            raise AuthenticationFailed(msg)

        return user


def payload_handler(user):
    """
    Add origin date to jwt payload
    :param user: User data
    :return: payload with the creation date
    """
    payload = jwt_payload_handler(user)
    payload['iat'] = datetime.utcnow()
    return payload
