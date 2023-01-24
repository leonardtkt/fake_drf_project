from django.http import HttpRequest
from django.views.generic.base import View

from rest_framework import permissions


class CreateOnly(permissions.BasePermission):
    """ Allow creation on new instance without authentication. Only other methods require
    authentication. Useful for user since will never be authenticated before creation of
    account. """

    def has_permission(self, request: HttpRequest, view: View) -> bool:
        return request.method == 'POST'
