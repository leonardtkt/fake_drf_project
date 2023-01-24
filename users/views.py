from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet

from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.validators import ValidationError

from requests.exceptions import HTTPError
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from drf_yasg.utils import swagger_auto_schema
import logging

from .permissions import CreateOnly
from .serializers import (
    UserSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    AccountVerifySerializer,
    SocialAuthInputSerializer,
    SocialAuthOutputSerializer,
)

logger = logging.getLogger('users')
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Lookup specific user by their id (depends on user permissions.)

    list:
        Lookup all users (depends on user permissions.)

    create:
        Register a new user.

    delete:
        Delete a user (depends on user permissions.)

    partial_update:
        Update one or more fields for a user using id (depends on user permissions.)

    update:
        Update all fields for a user using id (depends on user permissions.)
    """
    permission_classes = [IsAuthenticated | CreateOnly]
    serializer_class = UserSerializer

    def get_queryset(self) -> QuerySet:
        return User.objects.filter(id=self.request.user.id)

    @swagger_auto_schema(
        security=[],
        operation_id='users-create',
        operation_summary='Create new user',
    )
    def create(self, *args, **kwargs) -> Response:
        return super().create(*args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_id='users-validate-email',
        operation_summary='Validate a user\'s email address',
        query_serializer=AccountVerifySerializer,
        security=[],
        responses={
            200: 'Confirmation',
        })
    @action(detail=False, methods=['GET'], url_path='validate-email', permission_classes=[AllowAny])
    def validate_email(self, request: Request) -> Request:
        serializer = AccountVerifySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response({'detail': _('Votre compte est confirmé.')})


class SocialViewSet(viewsets.ViewSet):
    """ Things relating to logins using Facebook, Google, etc. """

    serializer_class = SocialAuthInputSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id='oauth2-login',
        operation_summary='Login via OAuth2 using external service',
        security=[],
        responses={200: SocialAuthInputSerializer()})
    def create(self, request: Request) -> Response:
        """ Authenticate a user by using a OAuth2 token provided from
        an external provider service like Facebook or Google. If successful,
        you will receive a JWT token for our API that you can add to your headers. """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.data.get('provider')
        access_token = serializer.data.get('access_token')

        strategy = load_strategy(request)

        try:
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
        except MissingBackend:
            return Response({'error': 'Please provide a valid provider.'}, status=400)

        # ensure that we've actually set the keys here or it throws a difficult error to deduce
        key, secret = backend.get_key_and_secret()
        if not key or not secret:
            logger.error(f'You need to set your environment variables! Without this we can\'t use {provider} for social auth!')
            return Response({'error': 'Provider needs additional setup before use.'}, status=400)

        try:
            user = backend.do_auth(access_token)
        except HTTPError as error:
            raise ValidationError({'error': 'invalid_token', 'details': str(error)})
        except AuthTokenError as error:
            raise ValidationError({'error': 'invalid_credentials', 'details': str(error)})

        try:
            authenticated_user = backend.do_auth(access_token, user=user)
        except (HTTPError, AuthForbidden) as error:
            raise ValidationError({'error': 'invalid_token', 'details': str(error)})
        except Exception as error:
            raise ValidationError({'error': 'invalid_token', 'details': f'{provider} - {error}'})

        if not authenticated_user or not authenticated_user.is_active:
            # UGLYHACK : replace google-oauth2 by googleoauth2 for frontend purpose
            provider_name = provider.replace('-', '')
            raise ValidationError({'error': 'invalid_token', 'details': provider_name})

        data = {
            'email': authenticated_user.email,
            'username': authenticated_user.username,
            'token': user.access_token  # jwt token
        }
        serializer = SocialAuthOutputSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)


@swagger_auto_schema(
    method='get',
    operation_id='me',
    operation_summary='Who am I?',
    responses={
        200: UserSerializer(),
        401: 'Not authenticated.'
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request: Request) -> Response:
    """ Get info for the currently logged in user. """

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    operation_id='password-reset-send',
    operation_summary='Send password reset email',
    operation_description='If a user is locked out of this account, call this to send reset email.',
    request_body=PasswordResetSerializer,
    security=[],
    responses={
        200: 'Confirmation',
    })
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset(request: Request) -> Response:
    """ Calls Django Auth PasswordResetForm save method.
    Accepts the following POST parameters: email
    Returns the success/fail message. """

    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    serializer.save()
    return Response({"detail": "Password reset e-mail has been sent."}, status=200)


@swagger_auto_schema(
    method='post',
    operation_id='password-reset-confirm',
    request_body=PasswordResetConfirmSerializer,
    operation_summary='New password from email link',
    operation_description='Pass in all the relevant information to set a new password for the locked-out user.',
    security=[],
    responses={
        200: 'Confirmation',
    })
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request: Request) -> Response:
    """ Password reset e-mail link is confirmed, therefore this resets the user's password.
    Accepts the following POST parameters: token, uid, new_password1, new_password2
    Returns the success/fail message. """

    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        {'detail': _('Password has been reset with the new password.')}
    )
