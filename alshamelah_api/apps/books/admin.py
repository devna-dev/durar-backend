from django.contrib import admin

from .models import Book, Thesis, Paper, BookAudio
from ..points.services import PointsService
from ..users.services import FCMService


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'approved',
    )
    exclude = ['data', 'type']
    readonly_fields = ('uploader',)

    def save_model(self, request, obj, form, change):
        if change:
            old = Book.objects.filter(pk=obj.pk).first()
            if not old.approved and obj.approved and old.uploader:
                FCMService.notify_book_approved(old.uploader)
                PointsService().book_approval_award(old.uploader, old.pk)
        super().save_model(request, obj, form, change)


@admin.register(Paper, Thesis)
class PaperAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'approved',
    )
    exclude = ['data', 'type', 'content']
    readonly_fields = ('uploader',)

    def save_model(self, request, obj, form, change):
        if change:
            if obj.type == 'paper':
                old = Paper.objects.filter(pk=obj.pk).first()
                if not old.approved and obj.approved and old.uploader:
                    FCMService.notify_paper_approved(old.uploader)
                    PointsService().paper_approval_award(old.uploader, old.pk)
            elif obj.type == 'thesis':
                old = Thesis.objects.filter(pk=obj.pk).first()
                if not old.approved and obj.approved and old.uploader:
                    FCMService.notify_thesis_approved(old.uploader)
                    PointsService().thesis_approved_award(old.uploader, old.pk)

        super().save_model(request, obj, form, change)


@admin.register(BookAudio)
class BookAudioAdmin(admin.ModelAdmin):
    list_display = (
        'get_name',
        'url',
        'approved',
    )
    exclude = ['type']
    readonly_fields = ('user',)

    def get_name(self, obj):
        return obj.book

    def save_model(self, request, obj, form, change):
        if change:
            if obj.type == 'audio':
                old = BookAudio.objects.filter(pk=obj.pk).first()
                if not old.approved and obj.approved and old.user:
                    FCMService.notify_audio_approved(old.user)
                    PointsService().book_approval_award(old.user, old.pk)

        super().save_model(request, obj, form, change)
