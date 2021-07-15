"""
api URL Configuration
"""
from django.conf import urls
from django.views.decorators.csrf import csrf_exempt

from api import root_schema
from api.urls import urlpatterns as urls_prod
from api.utils.schema_dev import GraphQLViewExploratory, AdminGraphQLViewExploratory

urlpatterns = urls_prod + [
    urls.url(r'^dev/', csrf_exempt(GraphQLViewExploratory.as_view(graphiql=True, schema=root_schema.SCHEMA))),
    urls.url(r'^dev_admin/', csrf_exempt(AdminGraphQLViewExploratory.as_view(graphiql=True,
                                                                             schema=root_schema.ADMIN_SCHEMA))),
]
