import datetime

from django.contrib import admin
from django.db.models import Q

from .models import Seminar, Discussion, DiscussionRegistration, SeminarRegistration, ArchivedSeminar, \
    ArchivedDiscussion, ArchivedDiscussionRegistration, ArchivedSeminarRegistration


@admin.register(Seminar, Discussion)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'lecturer',
        'date',
        'from_time',
        'to_time'
    )
    exclude = ['type']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(Q(date__gt=datetime.datetime.now().date()) | Q(
            Q(date=datetime.datetime.now().date()) & Q(from_time__gt=datetime.datetime.now().time())))


@admin.register(ArchivedSeminar, ArchivedDiscussion)
class ArchivedChatRoomAdmin(ChatRoomAdmin):

    def get_queryset(self, request):
        qs = super(ChatRoomAdmin, self).get_queryset(request)
        qs = qs.filter(Q(date__lt=datetime.datetime.now().date()) | Q(
            Q(date=datetime.datetime.now().date()) & Q(from_time__lte=datetime.datetime.now().time())))
        return qs

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(DiscussionRegistration, SeminarRegistration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'room_name',
        'user_name',
        'room_date',
        'room_from_time'
    )
    exclude = ['type']

    def room_name(self, obj):
        return obj.chat_room.title

    def user_name(self, obj):
        return obj.user

    def room_date(self, obj):
        return obj.chat_room.date

    def room_from_time(self, obj):
        return obj.chat_room.from_time

    def get_queryset(self, request):
        qs = super(RegistrationAdmin, self).get_queryset(request)
        return qs.filter(Q(chat_room__date__gt=datetime.datetime.now().date()) | Q(
            Q(chat_room__date=datetime.datetime.now().date()) & Q(chat_room__from_time__gt=datetime.datetime.now().time())))


@admin.register(ArchivedDiscussionRegistration, ArchivedSeminarRegistration)
class ArchivedRegistrationAdmin(RegistrationAdmin):

    def get_queryset(self, request):
        qs = super(RegistrationAdmin, self).get_queryset(request)
        return qs.filter(Q(chat_room__date__lt=datetime.datetime.now().date()) | Q(
            Q(chat_room__date=datetime.datetime.now().date()) & Q(chat_room__from_time__lte=datetime.datetime.now().time())))

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
