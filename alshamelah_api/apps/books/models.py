import os
from mutagen.mp3 import MP3
from datetime import datetime

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from .managers import BookAudioManager, BookPDFManager, PaperManager, ThesisManager, BookManager
from ..core.models import BaseModel


class Book(BaseModel):
    objects = BookManager()
    BOOK_TYPE_CHOICES = Choices(
        ('book', _(u'Book')),
        ('paper', _(u'Paper')),
        ('thesis', _(u'Thesis')),
    )

    def get_path(self, filename):
        return os.path.join(
            self.path,
            'cover-image',
            filename
        )

    title = models.CharField(max_length=100, verbose_name=_(u'Title'), null=False, blank=False)
    content = JSONField(verbose_name=_(u'Content'), null=True, blank=True)
    data = JSONField(null=True, blank=True)
    author = models.ForeignKey('authors.Author', related_name='books', verbose_name=_(u'Author'), null=True,
                               on_delete=models.SET_NULL)
    uploader = models.ForeignKey('users.User', related_name='books', verbose_name=_(u'Uploader'), null=True,
                                 on_delete=models.SET_NULL)
    category = models.ForeignKey('categories.Category', related_name='books', verbose_name=_(u'Category'), null=True,
                                 on_delete=models.SET_NULL)
    sub_category = models.ForeignKey('categories.SubCategory', related_name='books', verbose_name=_(u'Sub Category'),
                                     null=True,
                                     on_delete=models.SET_NULL)
    # has_audio = models.BooleanField(verbose_name=_(u'Has Audio'), default=False, null=True)
    approved = models.BooleanField(verbose_name=_(u'Approved'), default=False, null=True)
    publish_date = models.DateField(null=True, blank=True, verbose_name=_(u'Publish Date'))
    cover_image = models.ImageField(
        upload_to=get_path,
        blank=False,
        null=True
    )
    # read_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Read Count'))
    # download_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Download Count'))
    page_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Page Count'))
    description = models.CharField(max_length=2000, verbose_name=_(u'Description'), null=True, blank=False)
    type = models.CharField(max_length=10, choices=BOOK_TYPE_CHOICES, verbose_name=_(u'Type'))

    # search_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Search Count'))
    @property
    def image(self):
        return self.cover_image.url if self.cover_image else os.path.join(settings.MEDIA_URL, 'books',
                                                                          'default-cover.jpg')

    @property
    def pages(self):
        return self.content if self.content else None

    @property
    def path(self):
        if not self.pk:
            return None
        return os.path.join(self.type + ('s' if not self.type.endswith('s') else ''), str(self.pk))

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            saved_image = self.cover_image
            self.cover_image = None
            super(Book, self).save(*args, **kwargs)
            self.cover_image = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(Book, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(Book, self).__init__(*args, **kwargs)
        if self.pk is None:
            self.type = 'book'


class Paper(Book):
    objects = PaperManager()

    class Meta:
        proxy = True
        ordering = ['-creation_time']

    def __init__(self, *args, **kwargs):
        super(Paper, self).__init__(*args, **kwargs)
        self.type = 'paper'


class Thesis(Book):
    objects = ThesisManager()

    class Meta:
        proxy = True
        ordering = ['-creation_time']

    def __init__(self, *args, **kwargs):
        super(Thesis, self).__init__(*args, **kwargs)
        self.type = 'thesis'


class BookReview(BaseModel):
    RATING_RANGE = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    )
    user = models.ForeignKey('users.User', related_name='reviews', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='reviews', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(verbose_name=_(u'Rating'), choices=RATING_RANGE, null=True)
    comment = models.TextField(verbose_name=_(u'Comment'), null=True)

    def __str__(self):
        return self.comment


class BookReviewLike(BaseModel):
    user = models.ForeignKey('users.User', related_name='likes', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    review = models.ForeignKey(BookReview, related_name='likes', verbose_name=_(u'Review'), null=False,
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + ' like:' + self.review.comment


class BookNote(BaseModel):
    user = models.ForeignKey('users.User', related_name='book_notes', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='book_notes', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name=_('Title'), null=True, blank=True)
    note = models.TextField(verbose_name=_(u'Note'), null=True, blank=False)
    page = models.PositiveSmallIntegerField(verbose_name=_(u'Page'), null=False)
    start = models.PositiveIntegerField(verbose_name=_(u'Start'), null=False)
    end = models.PositiveIntegerField(verbose_name=_(u'End'), null=False)
    tashkeel_start = models.PositiveIntegerField(verbose_name=_(u'Tashkeel Start'), null=False)
    tashkeel_end = models.PositiveIntegerField(verbose_name=_(u'Tashkeel End'), null=False)

    def __str__(self):
        return self.note


class BookMark(BaseModel):
    user = models.ForeignKey('users.User', related_name='book_marks', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='book_marks', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    page = models.PositiveSmallIntegerField(verbose_name=_(u'Page'))

    def __str__(self):
        return self.page


class BookMedia(BaseModel):
    MEDIA_CHOICES = Choices(
        ('audio', _(u'Audio')),
        ('pdf', _(u'PDF')),
    )

    def get_path(self, file):
        return os.path.join(self.book.path, self.type, file)

    user = models.ForeignKey('users.User', related_name='book_media', verbose_name=_(u'User'), null=True,
                             on_delete=models.SET_NULL)
    book = models.ForeignKey(Book, related_name='book_media', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    duration = models.DecimalField(null=True, blank=True, verbose_name=_(u'Audio duration'), max_digits=10,
                                   decimal_places=2)
    type = models.CharField(max_length=10, choices=MEDIA_CHOICES, verbose_name=_(u'Type'))
    url = models.FileField(verbose_name=_(u'Url'), upload_to=get_path)
    approved = models.BooleanField(verbose_name=_(u'Approved'), default=False)

    def __str__(self):
        return self.book.title + '(' + self.type + "):" + self.url.url


class BookAudio(BookMedia):
    objects = BookAudioManager()

    class Meta:
        proxy = True
        verbose_name_plural = 'Book audio files'

    def __init__(self, *args, **kwargs):
        super(BookMedia, self).__init__(*args, **kwargs)
        self.type = 'audio'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.url:
            try:
                audio = MP3(self.url)
                self.duration = audio.info.length / 60
            except:
                pass
        return super(BookAudio, self).save(force_insert, force_update, using, update_fields)


class BookPDF(BookMedia):
    objects = BookPDFManager()

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(BookMedia, self).__init__(*args, **kwargs)
        self.type = 'pdf'


class FavoriteBook(BaseModel):
    user = models.ForeignKey('users.User', related_name='favorite_books', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='favorite_books', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)

    def __str__(self):
        return (self.user.name if self.user and self.user.name else '') + ":" + (
            self.book.title if self.book and self.book.title else '')


class ReadBook(BaseModel):
    user = models.ForeignKey('users.User', related_name='reads', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='readers', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    page = models.PositiveSmallIntegerField(verbose_name=_('Page reached'), null=True, blank=False)
    finished = models.BooleanField(null=False, verbose_name=_('Finished'), default=False)

    def __str__(self):
        return (self.user.name if self.user and self.user.name else '') + ":" + (
            self.book.title if self.book and self.book.title else '')


class DownloadBook(BaseModel):
    user = models.ForeignKey('users.User', related_name='downloads', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='downloads', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)

    def __str__(self):
        return (self.user.name if self.user and self.user.name else '') + ":" + (
            self.book.title if self.book and self.book.title else '')


class ListenBook(BaseModel):
    user = models.ForeignKey('users.User', related_name='listens', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='listens', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)

    def __str__(self):
        return (self.user.name if self.user and self.user.name else '') + ":" + (
            self.book.title if self.book and self.book.title else '')


class ListenProgress(BaseModel):
    listen = models.ForeignKey(ListenBook, related_name='file_progress', verbose_name=_('File Progress'), null=False,
                               on_delete=models.CASCADE)
    audio = models.ForeignKey(BookAudio, related_name='file_progress', verbose_name=_(u'Audio'), null=True,
                              on_delete=models.SET_NULL)
    progress = models.PositiveSmallIntegerField(verbose_name=_('Progress'), null=True, validators=[MinValueValidator(0),
                                                                                                   MaxValueValidator(
                                                                                                       100)])


class SearchBook(BaseModel):
    user = models.ForeignKey('users.User', related_name='searches', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)

    title = models.CharField(max_length=100, verbose_name=_(u'Title'), null=True, blank=True)
    content = models.CharField(max_length=100, verbose_name=_(u'Content'), null=True, blank=True)
    author = models.ForeignKey('authors.Author', related_name='searches', verbose_name=_(u'Author'), null=True,
                               on_delete=models.SET_NULL)
    category = models.ForeignKey('categories.Category', related_name='searches', verbose_name=_(u'Category'), null=True,
                                 on_delete=models.SET_NULL)
    sub_category = models.ForeignKey('categories.SubCategory', related_name='searches', verbose_name=_(u'Sub Category'),
                                     null=True,
                                     on_delete=models.SET_NULL)
    has_audio = models.BooleanField(verbose_name=_('Has Audio'), null=True, default=None)
    from_year = models.IntegerField(verbose_name=_('From Year'), null=True)
    to_year = models.IntegerField(verbose_name=_('To Year'), null=True)
    sort = models.CharField(max_length=100, verbose_name=_('Sort'), null=True)
    page = models.IntegerField(verbose_name=_('Page'), null=True)
    page_size = models.IntegerField(verbose_name=_('Page Size'), null=True)

    def __str__(self):
        return self.user.name + " search @ " + str(self.creation_time)

    class Meta:
        ordering = ['-creation_time']


class BookSuggestion(BaseModel):
    user = models.ForeignKey('users.User', related_name='suggestions', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name=_(u'Title'), null=False, blank=False)
    author = models.CharField(max_length=1000, verbose_name=_(u'Author'), null=False, blank=False)
    publish_year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_(u'Publish Year'),
                                                    validators=[MinValueValidator(0),
                                                                MaxValueValidator(
                                                                    datetime.now().year)])
    url = models.URLField(verbose_name=_(u'Book Url'), null=False, blank=False)

    def __str__(self):
        return self.user.name + ":" + self.title + ('(%s)' % self.author)


class MarkPosition(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return {'start': self.start, 'end': self.end}

    def __repr__(self):
        return str(self)


@receiver(models.signals.post_delete, sender=Book)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.path:
        import shutil
        path = os.path.join(settings.MEDIA_ROOT, instance.path)
        if os.path.isdir(path):
            shutil.rmtree(path)
