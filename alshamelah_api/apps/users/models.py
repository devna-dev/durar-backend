from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', _(u'Male')),
        ('F', _(u'Female')),
    )

    MEMBERSHIP_CHOICES = (
        ('N', _(u'New')),
        ('A', _(u'Active')),
        ('G', _(u'Golden')),
        ('U', _(u'Ultimate')),
    )

    name = models.CharField(max_length=50, verbose_name=_(u'Name'), null=True, blank=True)
    phone = models.CharField(max_length=50, verbose_name=_(u'Phone number'),
                             blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True,
                                 verbose_name=_(u'Birth date'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, null=True,
                              blank=True, verbose_name=_(u'Gender'))
    membership = models.CharField(choices=MEMBERSHIP_CHOICES, max_length=1, null=True,
                                  blank=True, verbose_name=_(u'Membership'))

    address = models.CharField(max_length=1000, verbose_name=_(u'Address'),
                               blank=True)
    country = models.CharField(max_length=100, verbose_name=_(u'Country'),
                               blank=True)
    photo = models.ImageField(verbose_name=_(u'Photo'), null=True, blank=True)

    def __str__(self):
        return self.email
