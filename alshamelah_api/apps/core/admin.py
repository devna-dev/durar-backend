from django.conf import settings
from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    list_per_page = settings.ADMIN_LIST_PAGE_SIZE
