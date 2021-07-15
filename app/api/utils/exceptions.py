"""To manage exceptions"""
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from graphql.error import GraphQLError


class BaseError(GraphQLError):
    """
    Custom base graphql error
    """
    message = 'Base Error'
    code = 'base-error'

    def __init__(self, nodes=None, stack=None, source=None, positions=None, locations=None):
        super(BaseError, self).__init__(self.__class__.message, nodes, stack, source, positions, locations)
