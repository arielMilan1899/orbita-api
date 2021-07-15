# -*- coding: utf-8 -*-
"""
Graphql Schema definition for accounts App
"""
from __future__ import unicode_literals

import graphene
from django.contrib.auth.signals import user_logged_in
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation
from jwt_auth import settings as jwt_settings

from accounts.forms import UserLoginForm
from accounts.middleware import payload_handler
from accounts.models import User


class AdminUserType(DjangoObjectType):
    """
    User node for admin app
    """

    class Meta:
        """
        Meta class configuration
        """
        model = User
        exclude_fields = ()
        skip_registry = True
        use_connection = True


class LoginUserMutation(DjangoFormMutation):
    """
     Login payload with the following fields:

     token: authentication token.

     errors: errors description.

    """

    class Meta:
        """
        Meta class configuration
        """
        form_class = UserLoginForm

    token = graphene.String()
    user = graphene.Field(AdminUserType)

    @staticmethod
    def generate_token(user):
        """
        Generate token through payload.
        :return: Token string.
        """
        payload = payload_handler(user)
        return jwt_settings.JWT_ENCODE_HANDLER(payload)

    @classmethod
    def perform_mutate(cls, form, info):
        """
        Factory method of this mutation
        :param form: Django form
        :param info: Schema info
        :return: instance of this class
        """
        user = form.get_user()
        token = cls.generate_token(user)
        user_logged_in.send(sender=user.__class__, request=info.context, user=user)
        return cls(token=token, user=user)


class UserMutation:
    """
    Root Class of the accounts app mutations
    """
    login = LoginUserMutation.Field(description='Sign in an user')
