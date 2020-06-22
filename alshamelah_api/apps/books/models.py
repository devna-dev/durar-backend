import os

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField
from model_utils import Choices

from .managers import BookAudioManager, BookPDFManager


class Book(models.Model):

    def path(self, filename):
        return os.path.join(
            self.path,
            'cover-image',
            filename
        )

    title = models.CharField(max_length=100, verbose_name=_(u'Title'), null=False, blank=False)
    content = JSONField(verbose_name=_(u'Content'), null=True, blank=True)
    data = JSONField(null=True)
    author = models.CharField(max_length=1000, verbose_name=_(u'Author'), null=False, blank=False)
    author_id = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Author Id'))
    uploader = models.ForeignKey('users.User', related_name='books', verbose_name=_(u'Uploader'), null=True,
                                 on_delete=models.SET_NULL)
    category = models.ForeignKey('categories.Category', related_name='books', verbose_name=_(u'Category'), null=True,
                                 on_delete=models.SET_NULL)
    sub_category = models.ForeignKey('categories.SubCategory', related_name='books', verbose_name=_(u'Sub Category'),
                                     null=True,
                                     on_delete=models.SET_NULL)
    # has_audio = models.BooleanField(verbose_name=_(u'Has Audio'), default=False, null=True)
    approved = models.BooleanField(verbose_name=_(u'Approved'), default=False, null=True)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)
    publish_date = models.DateField(null=True, blank=True, verbose_name=_(u'Publish Date'))
    cover_image = ThumbnailerImageField(
        upload_to=path,
        blank=True,
        null=True,
        resize_source=dict(size=(100, 100))
    )
    # read_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Read Count'))
    # download_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Download Count'))
    page_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Page Count'))

    # search_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(u'Search Count'))

    @property
    def pages(self):
        return self.content if self.content else None

    @property
    def path(self):
        if not self.pk:
            return None
        return os.path.join('books', str(self.pk))

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


class BookReview(models.Model):
    user = models.ForeignKey('users.User', related_name='book_reviews', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='book_reviews', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    comment = models.TextField(verbose_name=_(u'Comment'), null=False, blank=False)

    def __str__(self):
        return self.comment


class BookReviewLike(models.Model):
    user = models.ForeignKey('users.User', related_name='likes', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    review = models.ForeignKey(BookReview, related_name='likes', verbose_name=_(u'Review'), null=False,
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + ' like:' + self.review.comment


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
    start = models.PositiveIntegerField(verbose_name=_(u'Start'))
    highlighted_text = models.TextField(verbose_name=_(u'Highlighted Text'))

    def __str__(self):
        return "page:{page} highlighted:{highlight} ".format(page=self.page, highlight=self.highlighted_text)


class BookMedia(models.Model):
    MEDIA_CHOICES = Choices(
        ('audio', _(u'Audio')),
        ('pdf', _(u'PDF')),
    )

    def path(self, file):
        return os.path.join(self.book.path, self.type, file)

    user = models.ForeignKey('users.User', related_name='book_media', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='book_media', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=MEDIA_CHOICES, verbose_name=_(u'Type'))
    url = models.FileField(verbose_name=_(u'Url'), upload_to=path)
    approved = models.BooleanField(verbose_name=_(u'Approved'), default=False)

    def __str__(self):
        return self.type + ":" + self.url.url


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


class FavoriteBook(models.Model):
    user = models.ForeignKey('users.User', related_name='favorite_books', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='favorite_books', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + ":" + self.book.title


class ReadBook(models.Model):
    user = models.ForeignKey('users.User', related_name='reads', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='readers', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.name + ":" + self.book.title


class DownloadBook(models.Model):
    user = models.ForeignKey('users.User', related_name='downloads', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='downloads', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.name + ":" + self.book.title


class ListenBook(models.Model):
    user = models.ForeignKey('users.User', related_name='listens', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='listens', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.name + ":" + self.book.title


class SearchBook(models.Model):
    user = models.ForeignKey('users.User', related_name='searches', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='searches', verbose_name=_(u'Book'), null=False,
                             on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.name + ":" + self.book.title


class BookSuggestion(models.Model):
    user = models.ForeignKey('users.User', related_name='suggestions', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name=_(u'Title'), null=False, blank=False)
    author = models.CharField(max_length=1000, verbose_name=_(u'Author'), null=False, blank=False)
    publish_date = models.DateField(null=True, blank=True, verbose_name=_(u'Publish Date'))
    url = models.URLField(verbose_name=_(u'Book Url'), null=False, blank=False)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.name + ":" + self.title + ('(%s)' % self.author)


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
