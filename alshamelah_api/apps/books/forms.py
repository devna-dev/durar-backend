import json

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Book, BookPDF


class BookForm(forms.ModelForm):
    json_file = forms.FileField(allow_empty_file=False, required=False)
    pdf = forms.FileField(allow_empty_file=False, required=False)
    content = forms.CharField(required=False,widget=forms.HiddenInput())

    class Meta:
        model = Book
        exclude = ['type']
        readonly_fields = ('uploader', 'content', 'data', 'page_count')

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if self.files.get('content', None):
            self.fields['content'].required = False
            self.fields['content'].widget = forms.HiddenInput()
            self.fields['content'].widget.attrs['readonly'] = 'readonly'
        if self.files.get('data', None):
            self.fields['data'].required = False
            self.fields['data'].widget.attrs['readonly'] = 'readonly'
        if self.files.get('page_count', None):
            self.fields['page_count'].required = False
            self.fields['page_count'].widget.attrs['disabled'] = 'disabled'
        self.pdf_file = None
        self.file = None

    def clean(self):
        file = self.cleaned_data.get('json_file', None)
        if file:
            try:
                self.cleaned_data['data'] = json.load(file)
                pages = self.cleaned_data['data']['pages']
                if not pages or len(pages) < 0:
                    raise forms.ValidationError(_('Invalid pages data'))
                self.cleaned_data['content'] = pages
                self.cleaned_data['page_count'] = len(pages)
                if 'description' not in self.cleaned_data['data'].keys() and self.cleaned_data['data']['meta'][
                    'betaka']:
                    self.cleaned_data['description'] = self.cleaned_data['data']['meta']['betaka']
            except:
                raise forms.ValidationError(_('Bad json file'))
            self.file = file
        pdf = self.cleaned_data.get('pdf', None)
        if pdf:
            self.pdf_file = pdf
        return self.cleaned_data

    def save(self, commit=True):
        if not self.pdf_file and not self.file:
            return super(BookForm, self).save(commit)
        saved = super(BookForm, self).save(commit)
        if saved:
            if self.file:
                if self.cleaned_data['data']:
                    saved.data = self.cleaned_data['data']
                    saved.content = self.cleaned_data['content']
                    saved.page_count = len(self.cleaned_data['data']['pages'])
            saved.save()
            if self.pdf_file:
                BookPDF.objects.create(url=self.pdf_file, approved=self.cleaned_data['approved'], book=saved)
        return saved


class PaperForm(BookForm):
    json_file = None
    pdf = forms.FileField(allow_empty_file=False, required=False)

    class Meta:
        model = Book
        exclude = ['type', 'content', 'data']
        readonly_fields = ('uploader',)


class BookChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}: {}".format(obj.type ,obj.title)