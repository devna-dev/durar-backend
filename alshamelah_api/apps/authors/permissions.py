# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from rest_framework import permissions


class CanManageAuthor(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        parent_permission = super(CanManageAuthor, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        parent_permission = super(CanManageAuthor, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True
