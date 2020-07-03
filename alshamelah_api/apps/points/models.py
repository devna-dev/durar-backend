from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from ..core.models import BaseModel


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
