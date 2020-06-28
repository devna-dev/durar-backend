from django.contrib import admin

from .models import Book, Thesis, Paper


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'approved',
    )
    exclude = ['data', 'type']
    readonly_fields = ('uploader',)


@admin.register(Paper, Thesis)
class PaperAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'approved',
    )
    exclude = ['data', 'type', 'content']
    readonly_fields = ('uploader',)
