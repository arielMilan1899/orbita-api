"""Api views"""
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django_redis.cache import DJANGO_REDIS_LOGGER
from graphene_django.views import GraphQLView

from api.root_schema import SCHEMA, ADMIN_SCHEMA
from api.utils.exceptions import BaseError

logger = logging.getLogger((DJANGO_REDIS_LOGGER or __name__))  # pylint: disable=C0103


class AdminRequiredMixin(LoginRequiredMixin):
    """Requires the viewer to be a staff member"""
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super(AdminRequiredMixin, self).dispatch(request, *args, **kwargs)


class CustomGraphQLView(GraphQLView):
    """Modified GraphQLView to handle error code"""

    def check_depth(self, request, query):
        """Check if the query have a valid depth"""

        backend = self.get_backend(request)
        document = backend.document_from_string(self.schema, query)
        ast = document.document_ast
        for definition in ast.definitions:
            # We are only interested in queries
            if definition.operation != 'query':
                continue

            depth = measure_depth(definition.selection_set)
            if depth > settings.MAX_QUERY_DEPTH:  # set your depth max here
                return False

        return True

    def get_response(self, request, data, show_graphiql=False):
        """Override get response to handle a high level cache"""
        query, _, _, _ = self.get_graphql_params(request, data)

        try:
            if not self.check_depth(request, query):
                # return response as None and 403 status_code
                return None, 403
        except Exception:  # pylint: disable=W0703
            pass

        return super(CustomGraphQLView, self).get_response(request, data, show_graphiql)

    @staticmethod
    def format_error(error):
        formatted_error = GraphQLView.format_error(error)
        if hasattr(error, 'original_error') and isinstance(error.original_error, BaseError):
            formatted_error['code'] = error.original_error.code

        return formatted_error


class AdminGraphQLView(AdminRequiredMixin, CustomGraphQLView):
    """View only available to staff members"""


def get_introspection_schema(request):
    """
    Endpoint for get the introspection schema
    """

    if request.user.is_authenticated and request.user.is_staff:
        app = request.GET.get('app')

        schema = ADMIN_SCHEMA if app == 'admin' else SCHEMA
        data = {'data': schema.introspect()}
        return JsonResponse(
            data,
            json_dumps_params={'separators': (',', ':')},
            status=200
        )

    raise PermissionDenied()


def measure_depth(selection_set, level=1):
    """Calculate measure depth"""
    max_depth = level
    for field in selection_set.selections:
        if field.selection_set:
            new_depth = measure_depth(field.selection_set, level=level + 1)
            if new_depth > max_depth:
                max_depth = new_depth
    return max_depth
