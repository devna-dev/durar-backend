import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from .enums import OTPStatus, OTPTypes

OTP_LENGTH = 6


class OTPManager(models.Manager):
    def generate(self, user):
        codes = self.model.objects.filter(user_id=user, verified=False)
        otp = next((i for i in codes if i.creation_time + datetime.timedelta(seconds=self.DEFAULT_EXPIRY)
                    >= timezone.now() and not i.verified), None)
        if otp: return otp
        code = Utilities.generate(OTP_LENGTH)
        return self.model.objects.create(code=code, user_id=user, verified=False)

    def verify(self, user, code, expiry_in_sec=None):
        if expiry_in_sec is None:
            expiry_in_sec = self.DEFAULT_EXPIRY
        codes = self.model.objects.filter(user_id=user, code=code)
        if not codes.exists():
            return OTPStatus.Invalid
        otp = next((i for i in codes if i.creation_time + datetime.timedelta(seconds=expiry_in_sec)
                    <= timezone.now() and not i.verified), None)
        if otp:
            otp.verified = True
            otp.save()
            return OTPStatus.Verified
        otp = next((i for i in codes if not i.verified), None)
        if otp:
            return OTPStatus.Expired
        return OTPStatus.Used


class EmailOTPManager(OTPManager):
    DEFAULT_EXPIRY = settings.EMAIL_OTP_EXPIRY

    def get_queryset(self):
        return super(EmailOTPManager, self).get_queryset().filter(
            type=OTPTypes.Email)

    def create(self, **kwargs):
        kwargs.update({'type': OTPTypes.Email})
        return super(EmailOTPManager, self).create(**kwargs)

    def update(self, **kwargs):
        kwargs.update({'type': str(OTPTypes.Email)})
        return super(EmailOTPManager, self).update(**kwargs)


class PhoneOTPManager(OTPManager):
    DEFAULT_EXPIRY = settings.PHONE_OTP_EXPIRY

    def get_queryset(self):
        return super(PhoneOTPManager, self).get_queryset().filter(
            type=OTPTypes.Phone)

    def create(self, **kwargs):
        kwargs.update({'type': OTPTypes.Phone})
        return super(PhoneOTPManager, self).create(**kwargs)

    def update(self, **kwargs):
        kwargs.update({'type': OTPTypes.Phone})
        return super(PhoneOTPManager, self).update(**kwargs)


class Utilities(object):

    @staticmethod
    def generate(length):
        # Python code to generate
        # random numbers and
        # append them to a list
        import random

        # Function to generate
        # and append them
        # start = starting range,
        # end = ending range
        # num = number of
        # elements needs to be appended
        res = []

        for j in range(length):
            res.append(str(random.randint(0, 9)))

        return ''.join(res)
