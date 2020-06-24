# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from rolepermissions.roles import AbstractUserRole


class AppPermissions(object):
    create_books = 'create_books'
    create_book_comment = 'create_book_comments'
    create_book_mark = 'create_book_marks'
    create_book_highlight = 'create_book_highlights'
    create_book_audio = 'create_book_audio'
    create_book_pdf = 'create_book_pdf'
    create_book_rating = 'create_book_ratings'
    create_book_review = 'create_book_review'
    edit_book_comment = 'edit_book_comments'
    edit_book_mark = 'edit_book_marks'
    edit_book_highlight = 'edit_book_highlights'
    edit_book_audio = 'edit_book_audio'
    edit_book_pdf = 'edit_book_pdf'
    edit_book_rating = 'edit_book_ratings'
    edit_book_review = 'edit_book_review'
    view_book_comments = 'view_book_comments'
    view_book_review = 'view_book_review'
    view_books = 'view_books'
    view_book_marks = 'view_book_marks'
    view_book_highlights = 'view_book_highlights'
    view_book_audio = 'view_book_audio'
    view_book_pdf = 'view_book_pdf'
    view_book_ratings = 'view_book_ratings'
    delete_book_comment = 'delete_book_comments'
    delete_book_mark = 'delete_book_marks'
    delete_book_highlight = 'delete_book_highlights'
    delete_book_audio = 'delete_book_audio'
    delete_book_pdf = 'delete_book_pdf'
    delete_book_rating = 'delete_book_ratings'
    delete_book_review = 'delete_book_review'
    edit_password = 'edit_password'
    verify_email = 'verify_email'
    verify_phone = 'verify_phone'
    create_categories = 'create_categories'
    edit_categories = 'edit_categories'
    view_categories = 'view_categories'
    edit_books = 'edit_books'
    delete_books = 'delete_books'
    submit_books = 'submit_books'
    submit_audio = 'submit_audio'
    view_chat_room = 'view_chat_room'
    create_chat_room = 'create_chat_room'
    edit_chat_room = 'edit_chat_room'
    delete_chat_room = 'delete_chat_room'
    edit_user_data = 'edit_user_data'


class User(AbstractUserRole):
    available_permissions = {
        AppPermissions.create_books: True,
        AppPermissions.view_books: True,
        AppPermissions.create_book_comment: True,
        AppPermissions.create_book_mark: True,
        AppPermissions.create_book_highlight: True,
        AppPermissions.create_book_audio: True,
        AppPermissions.create_book_pdf: True,
        AppPermissions.create_book_rating: True,
        AppPermissions.create_book_review: True,
        AppPermissions.edit_book_comment: True,
        AppPermissions.edit_book_mark: True,
        AppPermissions.edit_book_highlight: True,
        AppPermissions.edit_book_audio: True,
        AppPermissions.edit_book_pdf: True,
        AppPermissions.edit_book_rating: True,
        AppPermissions.edit_book_review: True,
        AppPermissions.view_book_comments: True,
        AppPermissions.view_book_marks: True,
        AppPermissions.view_book_highlights: True,
        AppPermissions.view_book_audio: True,
        AppPermissions.view_book_pdf: True,
        AppPermissions.view_book_ratings: True,
        AppPermissions.delete_book_comment: True,
        AppPermissions.delete_book_mark: True,
        AppPermissions.delete_book_highlight: True,
        AppPermissions.delete_book_audio: True,
        AppPermissions.delete_book_pdf: True,
        AppPermissions.delete_book_rating: True,
        AppPermissions.delete_book_review: True,
        AppPermissions.edit_password: True,
        AppPermissions.verify_email: True,
        AppPermissions.verify_phone: True,
        AppPermissions.edit_user_data: True,
        AppPermissions.view_chat_room: True
    }


class Reviewer(AbstractUserRole):
    available_permissions = {
        AppPermissions.submit_books: True,
    }


class ChatAdmin(AbstractUserRole):
    available_permissions = {
        AppPermissions.create_chat_room: True,
        AppPermissions.edit_chat_room: True,
        AppPermissions.delete_chat_room: True
    }


class Admin(AbstractUserRole):
    available_permissions = {
        AppPermissions.create_books: True,
        AppPermissions.create_categories: True,
        AppPermissions.edit_categories: True,
        AppPermissions.view_categories: True,
        AppPermissions.edit_books: True,
        AppPermissions.delete_books: True,
        AppPermissions.submit_books: True,
        AppPermissions.submit_audio: True,
        AppPermissions.create_chat_room: True,
        AppPermissions.edit_chat_room: True,
        AppPermissions.delete_chat_room: True
    }
    all_permissions = {}
    all_permissions.update(User.available_permissions)
    all_permissions.update(available_permissions)
    available_permissions = all_permissions
