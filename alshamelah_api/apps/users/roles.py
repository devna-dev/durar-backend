# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from rolepermissions.roles import AbstractUserRole


class role1(AbstractUserRole):
    available_permissions = {
        'create_categories': True,
        'delete_categories': True,
        'edit_categories': True,
        'view_categories': True,
    }


class role2(AbstractUserRole):
    available_permissions = {
        'create_categories': True,
        'edit_categories': True,
        'view_categories': True,
    }
