from django.conf import settings
from django.contrib import admin

from .models import PointSetting, PointBadge, Achievement


@admin.register(PointSetting)
class PointsSettingAdmin(admin.ModelAdmin):
    list_display = (
        'donation',
        'book_approved',
        'paper_approved',
        'thesis_approved',
        'audio_approved'
    )

    def has_add_permission(self, request):
        return request.user.email == settings.ADMIN_EMAIL

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PointBadge)
class PointBadgesAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'point_num'
    )

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'type',
        'title',
        'bronze',
        'silver',
        'gold',
        'diamond'
    )

    def has_add_permission(self, request):
        return request.user.email == settings.ADMIN_EMAIL

    def has_delete_permission(self, request, obj=None):
        return False
