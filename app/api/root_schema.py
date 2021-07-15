"""
Graphql Schema definition for api project
"""
import graphene
from graphene_django.debug import DjangoDebug

from accounts.schema import UserMutation
from accounts.schema_admin import AdminUserQuery, AdminUserMutation
from contact_info.schema import ContactInfoQuery, ContactInfoMutation
from contact_info.schema_admin import AdminMessageQuery, AdminContactInfoMutation
from offers.schema import CategoryQuery, OfferQuery, MaterialQuery
from offers.schema_admin import AdminOfferMutation, AdminOfferQuery, AdminCategoryQuery


class RootQuery(OfferQuery, CategoryQuery, MaterialQuery, ContactInfoQuery, graphene.ObjectType):
    """
    This class inherit from multiple queries Class of the project
    """
    debug = graphene.Field(DjangoDebug, name='_debug')


class RootMutation(UserMutation, ContactInfoMutation, graphene.ObjectType):
    """
    This class inherit from multiple mutation Class of the project
    """
    debug = graphene.Field(DjangoDebug, name='_debug')


class RootAdminQuery(AdminOfferQuery, AdminCategoryQuery, AdminUserQuery, MaterialQuery, ContactInfoQuery,
                     AdminMessageQuery, graphene.ObjectType):
    """
    This class inherit from multiple queries Class of the project
    """
    debug = graphene.Field(DjangoDebug, name='_debug')


class RootAdminMutation(AdminUserMutation, AdminOfferMutation, AdminContactInfoMutation, graphene.ObjectType):
    """
    This class inherit from multiple queries Class of the project
    """
    debug = graphene.Field(DjangoDebug, name='_debug')


SCHEMA = graphene.Schema(query=RootQuery, mutation=RootMutation)
ADMIN_SCHEMA = graphene.Schema(query=RootAdminQuery, mutation=RootAdminMutation)
