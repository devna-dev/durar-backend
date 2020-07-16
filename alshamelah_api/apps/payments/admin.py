from django.contrib import admin

from .models import Payment
from ..core.admin import BaseModelAdmin


@admin.register(Payment)
class PaymentAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'amount',
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
