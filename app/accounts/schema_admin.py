# -*- coding: utf-8 -*-
"""
Graphql Schema definition for accounts App
"""
from __future__ import unicode_literals

import graphene
from accounts.mixins import LoginRequiredMutation
from accounts.schema import AdminUserType


class LogoutUserMutation(LoginRequiredMutation, graphene.ClientIDMutation):
    """Logout mutation"""

    success = graphene.Boolean()

    class Input:
        """No input is necessary"""

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input_fields):
        """
        Update logged user's jwt_valid_after date
        :return: Success of operation
        """
        user = info.context.user
        user.reset_jwt_valid_after()
        return cls(success=True)


class AdminUserQuery:
    """
    Staff Class of the accounts app queries
    """
    me = graphene.Field(AdminUserType, description='Return the authenticated user')

    @classmethod
    def resolve_me(cls, instance, info):
        """
        Query resolution of me query
        :param instance: UserQuery instance
        :param info: Schema info
        :return: A logged user
        """
        return info.context.user


class AdminUserMutation:
    """
    Root Class of the admin user mutations
    """
    logout = LogoutUserMutation.Field(description='Sign out an logged-in user')
