# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from rest_framework import permissions
from rolepermissions.checkers import has_permission


class CanManageBook(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated() and request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, 'view_books')

        # 'POST' method creation
        if request.method == 'POST':
            return has_permission(request.user, 'create_books')

        # 'PUT/PATCH' method update
        if request.method in ['PUT', 'PATCH']:
            return has_permission(request.user, 'edit_books')

        # Deleting Books
        if request.method == 'DELETE' and has_permission(request.user, 'delete_books'):
            return True

        parent_permission = super(CanManageBook, self).has_permission(request, view)

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
        if request.user.is_authenticated() and request.user.is_superuser:
            return True

        # 'PUT' method, editing the rental items
        if request.method in ['PUT', 'PATCH'] and has_permission(request.user, 'edit_books'):
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        # Deleting rental items
        if request.method == 'DELETE' and has_permission(request.user, 'delete_books'):
            return True

        parent_permission = super(CanManageBook, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True
