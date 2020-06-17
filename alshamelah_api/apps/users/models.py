from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from .enums import OTPTypes
from .managers import EmailOTPManager, PhoneOTPManager


class User(AbstractUser):
    GENDER_CHOICES = Choices(
        ('M', _(u'Male')),
        ('F', _(u'Female')),
    )

    MEMBERSHIP_CHOICES = Choices(
        ('N', _(u'New')),
        ('A', _(u'Active')),
        ('G', _(u'Golden')),
        ('U', _(u'Ultimate')),
    )

    name = models.CharField(max_length=50, verbose_name=_(u'Name'), null=True, blank=True)
    phone_code = models.CharField(max_length=50, verbose_name=_(u'Phone code'),
                                  blank=True, null=True)
    phone = models.CharField(max_length=50, verbose_name=_(u'Phone number'),
                             blank=True, null=True)
    phone_verified = models.BooleanField(verbose_name=_(u'Phone Verified'), default=False)
    birthday = models.DateField(null=True, blank=True,
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


class OTP(models.Model):
    TYPE_CHOICES = Choices(
        (OTPTypes.Email, _(u'Email')),
        (OTPTypes.Phone, _(u'Phone')),
    )
    user = models.ForeignKey(User, related_name='otps', verbose_name=_(u'OTP'), on_delete=models.CASCADE)
    code = models.CharField(max_length=6, verbose_name=_(u'Code'), null=False)
    type = models.CharField(choices=TYPE_CHOICES, max_length=2, verbose_name=_(u'Gender'))
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)
    verified = models.BooleanField(verbose_name=_(u'Verified'))


class EmailOTP(OTP):
    objects = EmailOTPManager()

    class Meta:
        proxy = True


class PhoneOTP(OTP):
    objects = PhoneOTPManager()

    class Meta:
        proxy = True
