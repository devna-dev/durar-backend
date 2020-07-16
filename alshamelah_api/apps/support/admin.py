from django.contrib import admin

from .models import Support
from ..core.admin import BaseModelAdmin


@admin.register(Support)
class SupportAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'subject'
    )
