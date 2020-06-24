from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..core.models import BaseModel


class Author(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_(u'name'), null=False, blank=False)

    class Meta:
        verbose_name_plural = "Authors"
        ordering = ['name']

    def __str__(self):
        return self.name
