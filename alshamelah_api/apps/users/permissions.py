# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from rest_framework import permissions


class IsUser(permissions.IsAuthenticated):
    """
    This permission checks if the user data is for itself.

    """

    # from django.contrib.auth import get_user_model
    # from rolepermissions import roles

    # roles.assign_role(user=user, role=role)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsSuperAdmin(permissions.IsAdminUser):
    """
    This permission checks if the user data is for itself.
    """

    def has_permission(self, request, view):
        return super(IsSuperAdmin, self).has_permission(request, view) and request.user.is_superuser


class CanConfirmEmail(permissions.IsAuthenticated):
    """
    Write documentation
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

class CanConfirmPhone(permissions.IsAuthenticated):
    """
    Write documentation
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False
