from django.contrib import admin

from .models import Support


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'subject'
    )
