"""
api URL Configuration
"""
from django.conf import urls
from django.views.decorators.csrf import csrf_exempt

from api import root_schema
from api.views import CustomGraphQLView, AdminGraphQLView, get_introspection_schema

urlpatterns = [
    urls.url(r'^graphql/',
             csrf_exempt(CustomGraphQLView.as_view(graphiql=False, schema=root_schema.SCHEMA, batch=True, ))),
    urls.url(r'^graphql_admin/', csrf_exempt(AdminGraphQLView.as_view(graphiql=False, schema=root_schema.ADMIN_SCHEMA,
                                                                      batch=True))),
    urls.url(r'^graphql_introspection_schema', get_introspection_schema),
]
