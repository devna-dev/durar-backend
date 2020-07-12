from django.contrib import admin

from .models import Legal, AppUrls


@admin.register(Legal)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'policy',
        'terms'
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

@admin.register(AppUrls)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'google',
        'apple'
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False