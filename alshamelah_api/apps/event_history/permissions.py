# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from rest_framework import permissions


class CanManageUserHistory(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        # Allow list to all
        if request.method in ['GET'] and request.user.is_authenticated:
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        parent_permission = super(CanManageUserHistory, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET'] and request.user.is_authenticated:
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        parent_permission = super(CanManageUserHistory, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True
