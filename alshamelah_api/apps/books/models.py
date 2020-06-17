from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from .managers import BookAudioManager, BookPDFManager


class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name=_(u'Title'), null=False, blank=False)
    content = models.TextField(verbose_name=_(u'Content'), null=False, blank=False)
    data = JSONField()
    author = models.CharField(max_length=1000, verbose_name=_(u'Author'), null=False, blank=False)
    author_id = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Author Id'))
    uploader = models.ForeignKey('users.User', related_name='books', verbose_name=_(u'Uploader'), null=True,
                                 on_delete=models.SET_NULL)
    category = models.ForeignKey('categories.Category', related_name='books', verbose_name=_(u'Category'), null=True,
                                 on_delete=models.SET_NULL)
    sub_category = models.ForeignKey('categories.SubCategory', related_name='books', verbose_name=_(u'Sub Category'),
                                     null=True,
                                     on_delete=models.SET_NULL)
    has_audio = models.BooleanField(verbose_name=_(u'Has Audio'), default=False)
    approved = models.BooleanField(verbose_name=_(u'Approved'), default=False)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)
    publish_date = models.DateField(null=True, blank=True, verbose_name=_(u'Publish Date'))
    cover_image = models.ImageField(verbose_name=_(u'Cover Image'), null=True, blank=True)
    read_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Read Count'))
    download_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Download Count'))
    page_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Page Count'))
    search_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Search Count'))

    def __str__(self):
        return self.title


class BookRating(models.Model):
    RATING_RANGE = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    )

    user = models.ForeignKey('users.User', related_name='book_ratings', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='book_ratings', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(verbose_name=_(u'Rating'), choices=RATING_RANGE)

    def __str__(self):
        return self.rating


class BookComment(models.Model):
    user = models.ForeignKey('users.User', related_name='book_comments', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='book_comments', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    comment = models.TextField(verbose_name=_(u'Comment'), null=False, blank=False)
    page = models.PositiveSmallIntegerField(verbose_name=_(u'Page'))
    line = models.PositiveSmallIntegerField(verbose_name=_(u'Line'))

    def __str__(self):
        return self.comment


class BookMark(models.Model):
    user = models.ForeignKey('users.User', related_name='book_marks', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='book_marks', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    page = models.PositiveSmallIntegerField(verbose_name=_(u'Page'))

    def __str__(self):
        return self.page


class BookHighlight(models.Model):
    user = models.ForeignKey('users.User', related_name='book_highlights', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='book_highlights', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    page = models.PositiveSmallIntegerField(verbose_name=_(u'Page'))
    line = models.PositiveSmallIntegerField(verbose_name=_(u'Line'))
    start = models.PositiveIntegerField(verbose_name=_(u'Start'))
    end = models.PositiveIntegerField(verbose_name=_(u'End'))

    def __str__(self):
        return "page:{page} line:{line} from:{start} to:{end}".format(page=self.page, line=self.line,
                                                                      start=self.start, end=self.end)


class BookMedia(models.Model):
    MEDIA_CHOICES = Choices(
        ('audio', _(u'Audio')),
        ('pdf', _(u'PDF')),
    )

    user = models.ForeignKey('users.User', related_name='book_media', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='book_media', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=MEDIA_CHOICES, verbose_name=_(u'Type'))
    url = models.URLField(verbose_name=_(u'Url'))
    approved = models.BooleanField(verbose_name=_(u'Approved'))

    def __str__(self):
        return self.type + ":" + self.url


class BookAudio(BookMedia):
    objects = BookAudioManager()

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(BookMedia, self).__init__(*args, **kwargs)
        self.type = 'audio'


class BookPDF(BookMedia):
    objects = BookPDFManager()

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(BookMedia, self).__init__(*args, **kwargs)
        self.type = 'pdf'
