from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..core.models import BaseModel


class Legal(BaseModel):
    policy = models.TextField(verbose_name=_(u'Privacy Policy'), null=False, blank=False)
    terms = models.TextField(verbose_name=_(u'Terms & Conditions'), null=False, blank=False)

    class Meta:
        verbose_name_plural = "Privacy Policy, Terms & Conditions"

class AppUrls(BaseModel):
    google = models.CharField(max_length=1000, verbose_name=_('Google Play Store URL'))
    apple = models.CharField(max_length=1000, verbose_name=_('Apple Store URL'))

    class Meta:
        verbose_name_plural = "App Urls"
