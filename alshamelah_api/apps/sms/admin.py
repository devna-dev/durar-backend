from django.contrib import admin

from .models import SMS


@admin.register(SMS)
class SMSAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'phone',
        'content',
        'status'
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
