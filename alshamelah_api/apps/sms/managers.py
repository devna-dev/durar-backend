import json

from django.conf import settings
from django.db import models
from rest_framework.reverse import reverse
from twilio.rest import Client

from ..users.models import PhoneOTP


class SMSManager(models.Manager):
    def send_verification(self, user, phone, request):
        otp = PhoneOTP.objects.generate(user.id)
        content = 'Your ' + settings.SITE_NAME + ' verification code is: ' + otp.code

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=content,
            from_=settings.TWILIO_NUMBER,
            status_callback=reverse('sms_update_status', request=request),
            to=phone
        )
        response = {
            'error_code': message.error_code,
            'error_message': message.error_message,
            'date_created': str(message.date_created),
            'sid': message.sid,
            'status': message.status
        }
        create = self.model.objects.create(user=user, phone=phone, content=content, response=json.dumps(response),
                                           status=message.status, sid=message.sid)
        return create
