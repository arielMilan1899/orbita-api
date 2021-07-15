"""
Helpers to Graphql schemas in dev environment
"""
from api.views import AdminGraphQLView, CustomGraphQLView


class GraphQLViewExploratory(CustomGraphQLView):
    """
    Alternative template to keep token authentication in navigator
    """
    graphiql_template = 'graphiql_dev.html'


class AdminGraphQLViewExploratory(AdminGraphQLView, GraphQLViewExploratory):
    """View only available to staff members"""

    def dispatch(self, request, *args, **kwargs):
        if 'HTTP_REFERER' not in request.environ or '?' not in request.environ['HTTP_REFERER']:
            return GraphQLViewExploratory.dispatch(self, request, *args, **kwargs)
        return super(AdminGraphQLViewExploratory, self).dispatch(request, *args, **kwargs)
