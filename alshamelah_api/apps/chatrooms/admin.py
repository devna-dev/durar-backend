from django.contrib import admin

from .models import RoomType, Seminar, Discussion, DiscussionRegistration, SeminarRegistration


@admin.register(Seminar, Discussion)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'lecturer',
        'date',
        'from_time',
        'to_time'
    )
    exclude = ['type']


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


@admin.register(RoomType)
class ChatRoomTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
