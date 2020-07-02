from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..core.models import BaseModel


class Event(BaseModel):
    type = models.CharField(max_length=100, verbose_name=_(u'Type'), null=False, blank=False)
    action = models.CharField(max_length=100, verbose_name=_(u'Action'), null=False, blank=False)
    user = models.ForeignKey('users.User', related_name='history', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    data = JSONField()

    class Meta:
        verbose_name_plural = "User History"

    def __str__(self):
        return self.user.name
