from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework import viewsets

from drf_yasg.utils import swagger_auto_schema

from . import serializers, models

User = get_user_model()


class LanguageViewSet(viewsets.ViewSet):
    """ Returns possible languages from settings. """

    permission_classes = [AllowAny]

    def list(self, request, format=None):
        return Response(settings.LANGUAGES, status=200)


class HealthRateThrottle(AnonRateThrottle):
    """ Custom throttle logic that can be used in conjunction with any ViewSet. """

    def get_rate(self) -> str:
        """ How many hits period max? https://www.django-rest-framework.org/api-guide/throttling/ """

        return settings.HEALTH_RATE_THROTTLE


class HealthViewSet(viewsets.ViewSet):
    """ For health checks (i.e. intended to interface with AWS Elastic Load Balancer) """

    permission_classes = [AllowAny]
    serializer_class = serializers.HealthSerializer
    throttle_classes = [HealthRateThrottle]

    @swagger_auto_schema(
        operation_id='health',
        operation_summary='Check status of server',
        security=[],
        responses={
            200: serializers.HealthSerializer(),
        })
    def list(self, request: Request, format=None) -> Response:
        """ Indicates health of the server and key associated services. """

        serializer = self.serializer_class(data={})
        serializer.is_valid(raise_exception=True)
        if not all(serializer.data.values()):
            return Response(serializer.data, status=400)
        return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_id='globals',
    operation_summary='Fetch site configuration',
    responses={
        200: serializers.PublicGlobalSettingsSerializer(),
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_settings(request: Request) -> Response:
    """ When applicable, returns dynamic global parameters that have been set by an
    administrator in the backoffice. """

    try:
        pub_settings = models.PublicGlobalSettings.objects.get()
    except models.PublicGlobalSettings.DoesNotExist:
        return Response({})  # not set yet

    serializer = serializers.PublicGlobalSettingsSerializer(pub_settings)
    return Response(serializer.data)
