import json

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import SMSManager
from ..core.models import BaseModel


class SMS(BaseModel):
    objects = SMSManager()
    phone = models.CharField(max_length=100, verbose_name=_(u'Phone'), null=False, blank=False)
    user = models.ForeignKey('users.User', related_name='sms', verbose_name=_(u'User'), null=False,
                             on_delete=models.CASCADE)
    sid = models.CharField(max_length=100, verbose_name=_(u'SID'), null=False, blank=False)
    content = models.CharField(max_length=500, verbose_name=_(u'Message'), null=False, blank=False)
    status = models.CharField(max_length=100, verbose_name=_(u'Status'), null=False, blank=False)
    response = JSONField(null=True)

    class Meta:
        verbose_name_plural = "SMS"

    def __str__(self):
        return self.user.name + '(%s)' % self.to

    def username(self):
        return self.user.name

    @property
    def response_data(self):
        if isinstance(self.response, dict): return self.response
        return json.loads(self.response) if self.response else None
