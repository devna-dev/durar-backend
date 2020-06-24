from django.contrib import admin

from .models import ChatRoom, RoomType


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'type',
        'lecturer',
        'date',
        'from_time',
        'to_time'
    )


@admin.register(RoomType)
class ChatRoomTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
