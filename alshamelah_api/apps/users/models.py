from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

class CustomUser(AbstractUser):
    name = models.CharField(max_length=50, verbose_name=_(u'Name'), null=True, blank=True)
     
    def __str__(self):
        return self.email