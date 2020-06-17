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
        from alshamelah_api.apps.users.roles import AppPermissions
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, AppPermissions.view_books)

        # 'POST' method creation
        if request.method == 'POST':
            return has_permission(request.user, AppPermissions.create_books)

        # 'PUT/PATCH' method update
        if request.method in ['PUT', 'PATCH']:
            return has_permission(request.user, AppPermissions.edit_books)

        # Deleting Books
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_books):
            return True

        parent_permission = super(CanManageBook, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        from alshamelah_api.apps.users.roles import AppPermissions
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        # 'PUT' method, editing the rental items
        if request.method in ['PUT', 'PATCH'] and has_permission(request.user, AppPermissions.edit_books):
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        # Deleting rental items
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_books):
            return True

        parent_permission = super(CanManageBook, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True


class CanSubmitBook(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        from alshamelah_api.apps.users.roles import AppPermissions
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, AppPermissions.submit_books)

        # 'PUT/PATCH' method update
        if request.method in ['PUT']:
            return has_permission(request.user, AppPermissions.submit_books)

        parent_permission = super(CanSubmitBook, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        from alshamelah_api.apps.users.roles import AppPermissions
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        # 'PUT' method, editing the rental items
        if request.method in ['PUT', 'PATCH'] and has_permission(request.user, AppPermissions.submit_books):
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        parent_permission = super(CanSubmitBook, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True


class CanManageBookRating(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        from alshamelah_api.apps.users.roles import AppPermissions
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, AppPermissions.view_book_ratings)

        # 'POST' method creation
        if request.method == 'POST':
            return has_permission(request.user, AppPermissions.create_book_rating)

        # 'PUT/PATCH' method update
        if request.method in ['PUT', 'PATCH']:
            return has_permission(request.user, AppPermissions.edit_book_rating)

        # Deleting Books
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_rating):
            return True

        parent_permission = super(CanManageBookRating, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        from alshamelah_api.apps.users.roles import AppPermissions
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        # 'PUT' method, editing the rental items
        if request.method in ['PUT', 'PATCH'] and has_permission(request.user, AppPermissions.edit_book_rating):
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        # Deleting rental items
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_rating):
            return True

        parent_permission = super(CanManageBookRating, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True


class CanManageBookComment(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        from alshamelah_api.apps.users.roles import AppPermissions
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, AppPermissions.view_book_comments)

        # 'POST' method creation
        if request.method == 'POST':
            return has_permission(request.user, AppPermissions.create_book_comment)

        # 'PUT/PATCH' method update
        if request.method in ['PUT', 'PATCH']:
            return has_permission(request.user, AppPermissions.edit_book_comment)

        # Deleting Books
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_comment):
            return True

        parent_permission = super(CanManageBookComment, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        from alshamelah_api.apps.users.roles import AppPermissions
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        # 'PUT' method, editing the rental items
        if request.method in ['PUT', 'PATCH'] and has_permission(request.user, AppPermissions.edit_book_comment):
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        # Deleting rental items
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_comment):
            return True

        parent_permission = super(CanManageBookComment, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True


class CanManageBookHighlight(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        from alshamelah_api.apps.users.roles import AppPermissions
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, AppPermissions.view_book_highlights)

        # 'POST' method creation
        if request.method == 'POST':
            return has_permission(request.user, AppPermissions.create_book_highlight)

        # 'PUT/PATCH' method update
        if request.method in ['PUT', 'PATCH']:
            return has_permission(request.user, AppPermissions.edit_book_highlight)

        # Deleting Books
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_highlight):
            return True

        parent_permission = super(CanManageBookHighlight, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        from alshamelah_api.apps.users.roles import AppPermissions
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        # 'PUT' method, editing the rental items
        if request.method in ['PUT', 'PATCH'] and has_permission(request.user, AppPermissions.edit_book_highlight):
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        # Deleting rental items
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_highlight):
            return True

        parent_permission = super(CanManageBookHighlight, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True


class CanManageBookMark(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        from alshamelah_api.apps.users.roles import AppPermissions
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, AppPermissions.view_book_marks)

        # 'POST' method creation
        if request.method == 'POST':
            return has_permission(request.user, AppPermissions.create_book_mark)

        # 'PUT/PATCH' method update
        if request.method in ['PUT', 'PATCH']:
            return has_permission(request.user, AppPermissions.edit_book_mark)

        # Deleting Books
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_mark):
            return True

        parent_permission = super(CanManageBookMark, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        from alshamelah_api.apps.users.roles import AppPermissions
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        # 'PUT' method, editing the rental items
        if request.method in ['PUT', 'PATCH'] and has_permission(request.user, AppPermissions.edit_book_mark):
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        # Deleting rental items
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_mark):
            return True

        parent_permission = super(CanManageBookMark, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True


class CanManageBookAudio(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        from alshamelah_api.apps.users.roles import AppPermissions
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, AppPermissions.view_book_audio)

        # 'POST' method creation
        if request.method == 'POST':
            return has_permission(request.user, AppPermissions.create_book_audio)

        # 'PUT/PATCH' method update
        if request.method in ['PUT', 'PATCH']:
            return has_permission(request.user, AppPermissions.edit_book_audio)

        # Deleting Books
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_audio):
            return True

        parent_permission = super(CanManageBookAudio, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        from alshamelah_api.apps.users.roles import AppPermissions
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        # 'PUT' method, editing the rental items
        if request.method in ['PUT', 'PATCH'] and has_permission(request.user, AppPermissions.edit_book_audio):
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        # Deleting rental items
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_audio):
            return True

        parent_permission = super(CanManageBookAudio, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True


class CanManageBookPdf(permissions.IsAuthenticated):
    """
    Write documentation
    """

    # book_lookup = 'parent_lookup_book' case of parent child

    def has_permission(self, request, view):
        from alshamelah_api.apps.users.roles import AppPermissions
        # Allow list to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return has_permission(request.user, AppPermissions.view_book_pdf)

        # 'POST' method creation
        if request.method == 'POST':
            return has_permission(request.user, AppPermissions.create_book_pdf)

        # 'PUT/PATCH' method update
        if request.method in ['PUT', 'PATCH']:
            return has_permission(request.user, AppPermissions.edit_book_pdf)

        # Deleting Books
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_pdf):
            return True

        parent_permission = super(CanManageBookPdf, self).has_permission(request, view)

        if not parent_permission:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        from alshamelah_api.apps.users.roles import AppPermissions
        """
        Manages only permissions for editing and deleting the objects
        """

        # Allow get to all
        if request.method in ['GET']:
            return True

        # Superuser can manage all the objects
        if request.user.is_authenticated and request.user.is_superuser:
            return True

        # 'PUT' method, editing the rental items
        if request.method in ['PUT', 'PATCH'] and has_permission(request.user, AppPermissions.edit_book_pdf):
            return True

        # 'PUT' method, editing the rental items
        # Let user have access to a single object
        if request.method in permissions.SAFE_METHODS:
            return True

        # Deleting rental items
        if request.method == 'DELETE' and has_permission(request.user, AppPermissions.delete_book_pdf):
            return True

        parent_permission = super(CanManageBookPdf, self).has_permission(request, view)
        if not parent_permission:
            return False
        return True
