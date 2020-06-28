from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..core.models import BaseModel


class Legal(BaseModel):
    policy = models.TextField(verbose_name=_(u'Privacy Policy'), null=False, blank=False)
    terms = models.TextField(verbose_name=_(u'Terms & Conditions'), null=False, blank=False)

    class Meta:
        verbose_name_plural = "Privacy Policy, Terms & Conditions"
