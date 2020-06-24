import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField
from model_utils import Choices

from .enums import OTPTypes
from .managers import EmailOTPManager, PhoneOTPManager


class User(AbstractUser):
    def get_path(self, filename):
        return os.path.join(
            self.path,
            'photo',
            filename
        )

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
    photo = ThumbnailerImageField(
        upload_to=get_path,
        blank=True,
        null=True,
        resize_source=dict(size=(100, 100),
                           verbose_name=_(u'Photo'))
    )

    # photo = models.ImageField(verbose_name=_(u'Photo'), null=True, blank=True)

    @property
    def path(self):
        if not self.pk:
            return None
        return os.path.join('users', str(self.pk))

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.pk is None:
            saved_image = self.photo
            self.photo = None
            super(User, self).save(*args, **kwargs)
            self.photo = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(User, self).save(*args, **kwargs)


class OTP(models.Model):
    TYPE_CHOICES = Choices(
        (OTPTypes.Email, _(u'Email')),
        (OTPTypes.Phone, _(u'Phone')),
    )
    user = models.ForeignKey(User, related_name='otps', verbose_name=_(u'OTP'), on_delete=models.CASCADE)
    code = models.CharField(max_length=6, verbose_name=_(u'Code'), null=False)
    type = models.CharField(choices=TYPE_CHOICES, max_length=2, verbose_name=_(u'Type'))
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


class Note(models.Model):
    user = models.OneToOneField(User, related_name='notes', verbose_name=_(u'Notes'), on_delete=models.CASCADE)
    note = models.TextField(verbose_name=_(u'Note'), null=True, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)


class NotificationSetting(models.Model):
    user = models.OneToOneField(User, related_name='notification_setting', verbose_name=_(u'Notification Setting'),
                                on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)
    device_id = models.CharField(max_length=255, verbose_name=_(u'Device Id'))
    enabled = models.BooleanField(verbose_name=_(u'Enabled'), default=True, null=True)
    book_added = models.BooleanField(verbose_name=_(u'Book Added'), default=True, null=True)
    book_approved = models.BooleanField(verbose_name=_(u'Book Approved'), default=True, null=True)
    audio_approved = models.BooleanField(verbose_name=_(u'Audio Approved'), default=True, null=True)


class Notification(models.Model):
    TYPE_CHOICES = Choices(
        ('book_added', _(u'Book Added')),
        ('book_approved', _(u'Book Approved')),
        ('audio_approved', _(u'Audio Approved')),
    )
    user = models.ForeignKey(User, related_name='notifications', verbose_name=_(u'Notifications'),
                             on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)
    title = models.CharField(max_length=255, verbose_name=_(u'Title'))
    type = models.CharField(choices=TYPE_CHOICES, max_length=20, verbose_name=_(u'Type'))
    message = models.CharField(max_length=1000, verbose_name=_(u'Message'))
    read = models.BooleanField(verbose_name=_(u'Read'), default=False, null=True)

    class Meta:
        ordering = ['-read', '-creation_time']


@receiver(models.signals.post_delete, sender=User)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.path:
        import shutil
        path = os.path.join(settings.MEDIA_ROOT, instance.path)
        if os.path.isdir(path):
            shutil.rmtree(path)
