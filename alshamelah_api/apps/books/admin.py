from django.contrib import admin

from .forms import BookForm, PaperForm, BookChoiceField
from .models import Book, Thesis, Paper, BookAudio, BookPDF
from ..categories.models import SubCategory
from ..core.admin import BaseModelAdmin
from ..points.services import PointsService
from ..users.services import FCMService


@admin.register(Book)
class BookAdmin(BaseModelAdmin):
    change_form_template = 'books/admin/change_form.html'
    add_form_template = change_form_template
    form = BookForm
    list_display = (
        'id',
        'title',
        'category',
        'approved',
    )
    exclude = ['type', 'data', 'content']
    readonly_fields = ('page_count', 'uploader',)

    def save_model(self, request, obj, form, change):
        if change:
            old = Book.objects.filter(pk=obj.pk).first()
            if not old.approved and obj.approved and old.uploader:
                FCMService.notify_book_approved(old.uploader)
                PointsService().book_approval_award(old.uploader, old.pk)
        super().save_model(request, obj, form, change)

    def get_all_sub_categories(self):
        types = SubCategory.objects.all().order_by('name').only('id', 'name', 'category_id')
        return ','.join(["{'id': '" + str(t.id) + "', 'name': '" + t.name + "', 'category_id': " + (
            str(t.category_id) if t.category_id else 'null') + "}" for t in types])

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['all_sub_categories'] = self.get_all_sub_categories()
        return super(BookAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['all_sub_categories'] = self.get_all_sub_categories()
        return super(BookAdmin, self).change_view(request, object_id, form_url, extra_context)


@admin.register(Paper, Thesis)
class PaperAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'approved',
    )
    exclude = ['data', 'type', 'content', 'sub_category']
    readonly_fields = ('uploader',)
    form = PaperForm

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


@admin.register(BookPDF)
class BookPDFAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'book_name',
        'book_type',
        'url',
        'approved',
    )
    exclude = ['type', 'duration']
    readonly_fields = ('user',)

    def book_name(self, obj):
        return obj.book

    def book_type(self, obj):
        return obj.book.type

    def save_model(self, request, obj, form, change):
        if change:
            if obj.type == 'audio':
                old = BookAudio.objects.filter(pk=obj.pk).first()
                if not old.approved and obj.approved and old.user:
                    FCMService.notify_audio_approved(old.user)
                    PointsService().book_approval_award(old.user, old.pk)

        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "book":
            return BookChoiceField(Book.objects.get_all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(BookAudio)
class BookAudioAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'book_name',
        'book_type',
        'url',
        'approved',
    )
    exclude = ['type', 'duration']
    readonly_fields = ('user',)

    def book_name(self, obj):
        return obj.book

    def book_type(self, obj):
        return obj.book.type

    def save_model(self, request, obj, form, change):
        if change:
            if obj.type == 'audio':
                old = BookAudio.objects.filter(pk=obj.pk).first()
                if not old.approved and obj.approved and old.user:
                    FCMService.notify_audio_approved(old.user)
                    PointsService().book_approval_award(old.user, old.pk)

        super().save_model(request, obj, form, change)
