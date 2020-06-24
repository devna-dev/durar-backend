from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..core.models import BaseModel


class Support(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_(u'Name'), null=False, blank=False)
    email = models.EmailField(max_length=100, verbose_name=_(u'Email'), null=False, blank=False)
    subject = models.CharField(max_length=100, verbose_name=_(u'Subject'), null=False, blank=False)
    message = models.CharField(max_length=8000, verbose_name=_(u'Message'), null=False, blank=False)

    class Meta:
        verbose_name_plural = "Support"

    def __str__(self):
        return self.name + ('(%s): ' % self.email) + self.subject
