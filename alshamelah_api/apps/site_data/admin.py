from django.contrib import admin

from .models import Legal


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
