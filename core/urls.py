from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from api.schema import schema
import graphql_jwt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    # path('api/token-auth/', graphql_jwt.views.ObtainJSONWebToken.as_view(), name='token_auth'),
    # path('api/token-verify/', graphql_jwt.views.VerifyToken.as_view(), name='token_verify'),
    # path('api/token-refresh/', graphql_jwt.views.RefreshToken.as_view(), name='token_refresh'),
]
