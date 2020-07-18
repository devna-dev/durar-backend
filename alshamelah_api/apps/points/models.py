import os

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from ..core.models import BaseModel
from ..users.services import FCMService


class PointSetting(BaseModel):
    donation = models.PositiveSmallIntegerField(verbose_name=_(u'Points per USD'), null=False, blank=False)
    book_approved = models.PositiveSmallIntegerField(verbose_name=_(u'Points per book approved'), null=False,
                                                     blank=False)
    paper_approved = models.PositiveSmallIntegerField(verbose_name=_(u'Points per paper approved'), null=False,
                                                      blank=False)
    thesis_approved = models.PositiveSmallIntegerField(verbose_name=_(u'Points per thesis approved'), null=False,
                                                       blank=False)
    audio_approved = models.PositiveSmallIntegerField(verbose_name=_(u'Points per book audio approved'), null=False,
                                                      blank=False)

    class Meta:
        verbose_name_plural = "Point Settings"

    def __str__(self):
        return "Point Settings"


class UserPoints(BaseModel):
    AWARD_TYPE_CHOICES = Choices(
        ('donation', _(u'Donation')),
        ('book_approved', _(u'Book Approval')),
        ('paper_approved', _(u'Paper Approval')),
        ('thesis_approved', _(u'Thesis Approval')),
        ('audio_approved', _(u'Book Audio Approval')),
    )
    user = models.ForeignKey('users.User', related_name='points', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    point_num = models.PositiveSmallIntegerField(verbose_name=_(u'Awarded points'), null=False)
    type = models.CharField(max_length=20, choices=AWARD_TYPE_CHOICES, verbose_name=_(u'Awarded For'))
    action_id = models.PositiveIntegerField(verbose_name=_(U'Transaction Id'), null=True, blank=False)

    class Meta:
        verbose_name_plural = 'User Points'


class PointBadge(BaseModel):
    name = models.CharField(max_length=500, verbose_name=_(u'Name'), null=False, blank=False)
    point_num = models.PositiveSmallIntegerField(verbose_name=_(u'Required points'), null=False)

    class Meta:
        verbose_name_plural = 'Point Badges'
        ordering = ['-point_num']


class Achievement(BaseModel):
    TYPE_CHOICES = Choices(
        ('pages_read_number', _(u'Reading x number of pages')),
        ('books_read_finished', _(u'Finishing x number of books (Physical books)')),
        ('writing_review', _(u'Writing a review on the book (Per Book)')),
        ('writing_note', _(u'Write a note (in the notepad or in the book) Per note')),
        ('highlighting_text', _(u'Highlighting text in a book')),
        ('making_bookmark', _(u'Bookmarking a page in a book - per bookmark')),
        ('attending_lecture', _(u'Attending a lecture')),
        ('rating_book', _(u'Review / rate a book or audio book (Like or dislike)')),
        ('share_book', _(u'Share book')),
        ('share_app', _(u'Share App')),
        ('share_lecture', _(u'Share lecture')),
        ('share_highlight', _(u'Share Highlighted text from book')),
        ('donation', _(u'Donating (Number of times donated)')),
        ('consecutive_daily_usage', _(u'Using the app daily for x amount of consecutive days(Once a day per day)')),
        ('minutes_listened', _(u'Listening to x number of minutes of audio book (Accumulated in minutes)')),
        ('books_listened', _(u'Finishing x number of audio books')),
        ('books_with_most_pages_finished',
         _(u'Finishing a book that is at least x number of pages (books of 100 pages +)')),
        ('books_with_most_minutes_finished',
         _(u'Finishing an audio book that is at least x number of minutes (120 Minutes +)')),
        ('books_read_number', _(u'Read part of x number of books - physical book')),
        ('books_listen_number',
         _(u'Listen to part of x number of audio books (jumping from one book to another) - audio')),
        ('daily_books_read_number',
         _(u'Read part of x number of books in one day (Jumping from one book to another in one day)')),
        ('daily_books_listen_number', _(u'Listen to part of x number of audio books in one day - same for audio')),
    )

    def get_path(self, filename):
        return os.path.join(
            'achievements',
            self.type,
            'icons',
            filename
        )

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name=_(u'Type'))
    title = models.CharField(max_length=200, verbose_name=_(u'Achievement Title'), null=False, blank=False)
    bronze = models.PositiveSmallIntegerField(verbose_name=_('Required number for bronze'))
    silver = models.PositiveSmallIntegerField(verbose_name=_('Required number for silver'))
    gold = models.PositiveSmallIntegerField(verbose_name=_('Required number for gold'))
    diamond = models.PositiveSmallIntegerField(verbose_name=_('Required number for diamond'))
    default_icon = models.ImageField(verbose_name=_(u'Default Achievement Icon'), upload_to=get_path)
    bronze_icon = models.ImageField(verbose_name=_(u'Bronze Achievement Icon'), upload_to=get_path)
    silver_icon = models.ImageField(verbose_name=_(u'Silver Achievement Icon'), upload_to=get_path)
    gold_icon = models.ImageField(verbose_name=_(u'Gold Achievement Icon'), upload_to=get_path)
    diamond_icon = models.ImageField(verbose_name=_(u'Diamond Achievement Icon'), upload_to=get_path)

    def __str__(self):
        return '{}: {}'.format(self.TYPE_CHOICES[self.type], self.title)

    class Meta:
        ordering = ['creation_time']


class UserAchievement(BaseModel):
    user = models.ForeignKey('users.User', related_name='achievements', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, related_name='achievements', verbose_name=_(u'Achievement'), null=True,
                                    on_delete=models.SET_NULL)
    TYPE_CHOICES = Choices(
        ('bronze', _(u'Bronze')),
        ('silver', _(u'Silver')),
        ('gold', _(u'Gold')),
        ('diamond', _(u'Diamond')),
    )

    category = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name=_(u'Type'))
    points = models.PositiveSmallIntegerField(default=0, null=False)

    @property
    def title(self):
        return self.achievement.title

    @property
    def icon(self):
        return getattr(self.achievement, self.category + '_icon').url

    @property
    def type(self):
        return self.achievement.type

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        saved = super(UserAchievement, self).save(force_insert, force_update, using, update_fields)
        FCMService.notify_achievement_awarded(self.user, self)
        return saved


class UserStatistics(BaseModel):
    from .managers import UserStatisticsManager
    objects = UserStatisticsManager()
    user = models.ForeignKey('users.User', related_name='statistics', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    reads = JSONField(null=True)  #
    book_note_count = models.PositiveSmallIntegerField(default=0)
    user_note_count = models.PositiveSmallIntegerField(default=0)
    book_highlight_count = models.PositiveSmallIntegerField(default=0)
    book_mark_count = models.PositiveSmallIntegerField(default=0)
    book_finished_count = models.PositiveSmallIntegerField(default=0) #
    book_review_count = models.PositiveSmallIntegerField(default=0)
    book_rate_count = models.PositiveSmallIntegerField(default=0)
    book_share_count = models.PositiveSmallIntegerField(default=0)
    app_share_count = models.PositiveSmallIntegerField(default=0)
    lecture_share_count = models.PositiveSmallIntegerField(default=0)
    lecture_attendance_count = models.PositiveSmallIntegerField(default=0)
    highlight_share_count = models.PositiveSmallIntegerField(default=0)
    donation_count = models.PositiveSmallIntegerField(default=0)
    minutes_listened = models.PositiveSmallIntegerField(default=0)
    audio_book_finished_count = models.PositiveSmallIntegerField(default=0)
    book_read_count = models.PositiveSmallIntegerField(default=0) #
    page_read_count = models.PositiveSmallIntegerField(default=0) #
    book_listened_count = models.PositiveSmallIntegerField(default=0)
    max_book_pages_read = models.PositiveSmallIntegerField(default=0) #
    max_book_audio_minutes_listened = models.PositiveSmallIntegerField(default=0)
    max_consecutive_login_days = models.PositiveSmallIntegerField(default=0)
    max_daily_read = models.PositiveSmallIntegerField(default=0) #
    max_daily_listen = models.PositiveSmallIntegerField(default=0)
    daily_read = JSONField(null=True) #
    daily_listen = JSONField(null=True)
