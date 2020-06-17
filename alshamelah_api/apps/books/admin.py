from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'approved',
    )
    exclude = ['data']
    readonly_fields = ('uploader', 'read_count', 'download_count', 'search_count', 'has_audio')
