import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField
from model_utils import Choices

from .enums import OTPTypes
from .managers import EmailOTPManager, PhoneOTPManager, PasswordOTPManager


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

    name = models.CharField(max_length=50, verbose_name=_(u'Name'), null=True, blank=True)
    phone = models.CharField(max_length=50, verbose_name=_(u'Phone number'),
                             blank=True, null=True)
    phone_verified = models.BooleanField(verbose_name=_(u'Phone Verified'), default=False)
    birthday = models.DateField(null=True, blank=True,
                                verbose_name=_(u'Birth date'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, null=True,
                              blank=True, verbose_name=_(u'Gender'))
    # membership = models.CharField(choices=MEMBERSHIP_CHOICES, max_length=1, null=True,
    #                               blank=True, verbose_name=_(u'Membership'))

    address = models.CharField(max_length=1000, verbose_name=_(u'Address'),
                               blank=True)
    country = models.CharField(max_length=100, verbose_name=_(u'Country'),
                               blank=True)
    photo = ThumbnailerImageField(
        upload_to=get_path,
        blank=False,
        null=True,
        resize_source=dict(size=(120, 120),
                           verbose_name=_(u'Photo'))
    )

    # photo = models.ImageField(verbose_name=_(u'Photo'), null=True, blank=True)

    @property
    def path(self):
        if not self.pk:
            return None
        return os.path.join('users', str(self.pk))

    @property
    def photo_url(self):
        return self.photo.url if self.photo else os.path.join(settings.MEDIA_URL, 'users', 'avatar.jpg')

    @property
    def membership(self):
        from ..points.models import UserPoints, PointBadge
        points = UserPoints.objects.filter(user_id=self.id).aggregate(total=Sum('point_num'))
        if not points or not points['total']:
            return None
        badge = PointBadge.objects.filter(point_num__lte=points['total']).order_by('-point_num').first()
        return badge.name if badge else None

    def __str__(self):
        return '{name} ({email})'.format(name=self.name if self.name else '', email=self.email)

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
        (OTPTypes.Password, _(u'Passwod')),
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

class PasswordOTP(OTP):
    objects = PasswordOTPManager()

    class Meta:
        proxy = True

class Note(models.Model):
    user = models.ForeignKey(User, related_name='notes', verbose_name=_(u'Notes'), on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name=_('Title'), null=True, blank=True)
    note = models.TextField(verbose_name=_(u'Note'), null=True, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)


class DailyLogin(models.Model):
    user = models.ForeignKey(User, related_name='logins', verbose_name=_(u'logins'), on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)

class NotificationSetting(models.Model):
    user = models.OneToOneField(User, related_name='notification_setting', verbose_name=_(u'Notification Setting'),
                                on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)
    device_id = models.CharField(max_length=255, verbose_name=_(u'Device Id'))
    enabled = models.BooleanField(verbose_name=_(u'Enabled'), default=True, null=True)
    paper_approved = models.BooleanField(verbose_name=_(u'Paper Approved'), default=True, null=True)
    thesis_approved = models.BooleanField(verbose_name=_(u'Thesis Approved'), default=True, null=True)
    book_approved = models.BooleanField(verbose_name=_(u'Book Approved'), default=True, null=True)
    audio_approved = models.BooleanField(verbose_name=_(u'Audio Approved'), default=True, null=True)
    payment_processed = models.BooleanField(verbose_name=_(u'Payment Processed'), default=True, null=True)
    support_requested = models.BooleanField(verbose_name=_(u'Support Requested'), default=True, null=True)
    points_awarded = models.BooleanField(verbose_name=_(u'Points Awarded'), default=True, null=True)
    admin_notifications = models.BooleanField(verbose_name=_(u'Admin Notifications'), default=True, null=True)


class Notification(models.Model):
    TYPE_CHOICES = Choices(
        # ('book_added', _(u'Book Added')),
        ('book_approved', _(u'Book Approved')),
        ('paper_approved', _(u'Paper Approved')),
        ('thesis_approved', _(u'Thesis Approved')),
        ('audio_approved', _(u'Audio Approved')),
        ('payment_success', _(u'Payment Success')),
        ('payment_rejected', _(u'Payment Rejected')),
        ('support_request', _(u'Support Request')),
        ('points_awarded', _(u'Points awarded')),
        ('admin_notification', _(u'Admin Notification')),
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


class CustomNotification(models.Model):
    users = models.ManyToManyField(User, related_name='custom_notifications',
                                   verbose_name=_(u'Notify Users \n(with notification enabled)'))
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_update_time = models.DateTimeField(auto_now=True, null=True)
    title = models.CharField(max_length=255, verbose_name=_(u'Title'))
    message = models.CharField(max_length=1000, verbose_name=_(u'Message'))

    class Meta:
        ordering = ['-creation_time']


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
